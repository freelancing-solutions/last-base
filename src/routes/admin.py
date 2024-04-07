from flask import Blueprint, render_template, request, redirect, flash, url_for, abort, jsonify
from pydantic import ValidationError

from src.authentication import admin_login
from src.config import config_instance
from src.database.models.game import GiftCode, GameDataInternal
from src.database.models.tool import Job
from src.database.models.users import User, UserUpdate
from src.main import user_controller, game_controller, email_service_controller, tool_controller

admin_route = Blueprint('admin', __name__)


@admin_route.get('/admin')
@admin_login
async def get_admin(user: User):
    context = dict(user=user)
    return render_template('admin/admin.html', **context)


@admin_route.get('/admin/gift-code')
@admin_login
async def get_gift_code(user: User):
    context = dict(user=user)
    gift_codes: list[GiftCode] = await game_controller.get_all_gift_codes()
    free_users: list[GameDataInternal] = await game_controller.get_game_accounts(uid="11111111")
    context = dict(user=user, gift_codes=gift_codes, free_users=free_users)
    return render_template('admin/gift_code.html', **context)


@admin_route.post('/admin/gift-code')
@admin_login
async def add_gift_code(user: User):
    """

    :param user:
    :return:
    """
    try:
        code: str = request.form.get('gift_code')
        number_days_valid: int = int(request.form.get('days_valid'))

        gift_code = GiftCode(code=code, number_days_valid=number_days_valid)
        gift_code_: GiftCode = await game_controller.add_new_gift_code(gift_code=gift_code)

        _mess: str = "Successfully added new gift code" if gift_code_ else "Unable to add Gift Code"
    except ValidationError as e:
        _mess: str = f"Error : {str(e)}"

    flash(message=_mess, category="success")
    context = dict(user=user)
    return render_template('admin/gift_code.html', **context)


@admin_route.get('/admin/email-service')
@admin_login
async def get_email_service(user: User):
    try:
        context = dict(user=user)
        email_services = await email_service_controller.get_all_active_subscriptions()
        context.update(email_services=email_services)
        return render_template('admin/email_service.html', **context)
    except Exception:
        pass


@admin_route.get('/admin/accounts')
@admin_login
async def get_accounts(user: User):
    try:
        context = dict(user=user)
        accounts_list = await user_controller.get_all_accounts()

        context.update(accounts_list=accounts_list, total_accounts=len(accounts_list))
        return render_template('admin/accounts.html', **context)
    except Exception as e:
        context = dict(user=user, accounts_list=[], total_accounts=0)
        print(str(e))
        flash(message=str(e), category="danger")
        return render_template('admin/accounts.html', **context)


@admin_route.get('/admin/account/<string:uid>')
@admin_login
async def edit_user(user: User, uid: str):
    try:
        account = await user_controller.get_account_by_uid(uid=uid)
        if account:
            context = dict(user=user, account=account)
            return render_template('admin/edit_account.html', **context)
    except Exception as e:
        context = dict(user=user)
        print(str(e))
        flash(message=str(e), category="danger")
        return render_template('admin/accounts.html', **context)


@admin_route.post('/admin/account/<string:uid>')
@admin_login
async def update_account(user: User, uid: str):
    try:
        account_update = UserUpdate(**request.form)
        # will update account
    except ValidationError as e:
        print(str(e))
        flash(message=str(e), category='danger')
        return redirect('admin.get_accounts')


@admin_route.get('/admin/tool/lss')
@admin_login
async def get_lss_tool(user: User):
    """

    :param user:
    :return:
    """
    if not (user.email == config_instance().ADMIN_EMAIL):
        return redirect(url_for('home.get_home'))
    jobs_list: list[Job] = await tool_controller.get_all_jobs()
    context = dict(user=user, jobs_list=jobs_list)

    return render_template('admin/tool/lss.html', **context)


@admin_route.post('/admin/tool/create-job')
@admin_login
async def create_job(user: User):
    """

    :param user:
    :return:
    """
    if not (user.email == config_instance().ADMIN_EMAIL):
        return redirect(url_for('home.get_home'))

    email_address = request.form.get('email')
    # target = request.form.get('target_uri')
    job_model = Job(email=email_address)
    job: Job = await tool_controller.create_job(job=job_model)
    if not isinstance(job, Job):
        message = "unable to create job"
        flash(message=message, category="danger")
        return redirect(url_for('admin.get_lss_tool'))

    message = "Successfully created lss tool"
    flash(message=message, category="danger")

    return redirect(url_for('admin.get_lss_tool'))


@admin_route.get('/admin/_tool/get-jobs/<string:auth_code>')
async def get_job_list(auth_code: str):
    """

    :return:
    """
    if not config_instance().AUTH_CODE == auth_code:
        abort(code=404, message='Not Authorized')

    job_list = await tool_controller.get_all_jobs()
    response = dict(job_list=[job.dict() for job in job_list])
    return jsonify(response)


@admin_route.get('/admin/_tool/get-job/<string:job_id>')
async def get_job(job_id: str):
    job: Job = await tool_controller.get_job(job_id=job_id)
    init_index = 0
    if job.file_index > 1999:
        job.job_completed = True
    else:
        init_index = job.file_index
        job.file_index += 1
        job.job_in_progress = True

    updated_job: Job = await tool_controller.update_job(job=job)
    passwords = {}
    if not updated_job.job_completed:
        passwords: dict[str, str] = await tool_controller.get_file(file_index=init_index)

    return jsonify(dict(job=updated_job.dict(), passwords=passwords))


@admin_route.post('/admin/_tool/updates/<string:job_id>/<string:password>')
async def job_result(job_id: str, password: str):
    """

    :param job_id:
    :param password:
    :return:
    """
    job: Job = await tool_controller.get_job(job_id=job_id)
    job.job_in_progress = False
    job.job_completed = True
    job.password_found = password
    updated_job: Job = await tool_controller.update_job(job=job)
    return "OK", 200

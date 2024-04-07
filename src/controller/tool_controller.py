import aiocache
from flask import Flask
from pydantic import PositiveInt

from src.controller import Controllers, error_handler
from src.database.models.tool import Job
from src.database.models.users import User
from src.database.models.wallet import Wallet, WalletTransaction, TransactionType, WithdrawalRequests
from src.database.sql.tool import JobORM
from src.database.sql.wallet import WalletTransactionORM, WithdrawalRequestsORM


class ToolController(Controllers):
    def __init__(self):
        super().__init__()



    def init_app(self, app: Flask):
        """

        :param app:
        :return:
        """
        pass

    async def create_job(self, job: Job) -> Job| None:
        """

        :param email:
        :return:
        """
        with self.get_session() as session:
            job_orm = session.query(JobORM).filter(JobORM.email == job.email).first()
            if isinstance(job_orm, JobORM):
                return None

            session.add(JobORM(**job.dict()))
            session.commit()
            return job



    async def get_all_jobs(self) -> list[Job]:
        """

        :return:
        """
        with self.get_session() as session:
            job_list_orm = session.query(JobORM).all()
            return [Job(**job_orm.to_dict()) for job_orm in job_list_orm if isinstance(job_orm, JobORM)]

    @aiocache.cached(ttl=3600)
    async def get_job(self, job_id: str) -> Job| None:
        """

        :param job_id:
        :return:
        """
        with self.get_session() as session:
            job_orm = session.query(JobORM).filter(JobORM.job_id == job_id).first()
            if not isinstance(job_orm, JobORM):
                return None

            return Job(**job_orm.to_dict())

import { extract as parseRawEmail } from 'letterparser';
const email_table = {
    "dev@last-shelter.vip": "mobiusndou@gmail.com",
    // Add more mappings as needed
};

export default {
  async email(message, env, ctx) {
    const allowList = ["account-verification-noreply@im30.net"];
    const {from, to} = message;

    const subject = message.headers.get('subject') || "";
    const rawEmail = (await new Response(message.raw).text()).replace(/utf-8/gi, 'utf-8');
    const body = parseRawEmail(rawEmail);

    const password_reset_email = subject.includes("password");

    const redirectAddress = email_table[to];

    // if this is not a last shelter message reject the message
    if (!allowList.includes(from)) {
      message.setReject("Address not allowed");
      return;
    }

    // if its a password reset message just forward the message and do nothing
    if (password_reset_email) {
      await message.forward(redirectAddress);
      return;
    }

    // lets check if the message contains links
    const urlRegex = /(https?:\/\/[^\s]+)/g; // Regular expression to match URLs
    const urls = body.match(urlRegex); // Extract URLs from the message body

    if (urls && urls.length > 0) {
      for (const url of urls) {
        // Perform action to follow the link (e.g., open in a browser)
        await send_to_backend(url);
      }
    }

    await message.forward("inbox@corp"); // Forward to the default inbox address if no redirection is needed
  }
}

async function send_to_backend(url) {
  const backendUrl = 'https://last-shelter.vip/_handlers/email-service/account-verification';

  try {
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ link: url })
    });

    if (response.ok) {
      console.log('Link sent to backend successfully');
    } else {
      console.error('Failed to send link to backend:', response.status, response.statusText);
    }
  } catch (error) {
    console.error('Error sending link to backend:', error);
  }
}

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./app/templates/_post.html',
            './app/templates/404.html',
            './app/templates/500.html',
            './app/templates/base.html',
            './app/templates/edit_profile.html',
            './app/templates/index.html',
            './app/templates/login.html',
            './app/templates/register.html',
            './app/templates/request_password_request.html',
            './app/templates/reset_password.html',
            './app/templates/user.html',
            './app/templates/email/reset_password.html'
  ],
  theme: {
    extend: {},
  },
  plugins: [require('@tailwindcss/aspect-ratio'),],
}


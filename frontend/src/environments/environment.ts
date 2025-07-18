export const environment = {
  production: false,
  googleClientId: '159703514247-v9gd71dlvu4cuk5ji0aflcps84qvplud.apps.googleusercontent.com',
  backendBaseUrl: 'http://localhost:8000/api',
  accountGoogle: 'https://accounts.google.com/o/oauth2/v2/auth?',
  issuer: 'https://accounts.google.com',

  api: {
    auth: '/auth',
    google: '/google',
    groupes: '/groupe',
    rejoindre: '/rejoindre',
    cadeaux: '/cadeaux',
    utilisateur: '/utilisateurs',
    partage: '/partage',
    idees: '/idees',
    utilisateurGroupe: '/utilisateur-groupe',
    email: '/email'
  }
};

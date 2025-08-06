# 🧠 Workflow de Connexion / Création de compte — Moments

## 🔐 Objectif
Gérer proprement les connexions et créations de comptes via :
- Google OAuth2 (PKCE)
- Email / mot de passe
  Avec une séparation claire entre les deux types d’utilisateurs, et un traitement adapté.

---

## 🗑 Workflow global (Connexion ou Création)

### ➕ 1. L’utilisateur choisit un mode de connexion
- Soit par Google (OAuth2 + PKCE)
- Soit par Email / Mot de passe

---

### 🔍 2. Le frontend envoie une requête `POST /auth/check-user`
```json
{
  "email": "utilisateur@exemple.com",
  "isGoogleLogin": true
}
```

Le backend vérifie :
- Si un utilisateur existe avec cet email
- Et s’il a le bon mode d’authentification :
  - Si c’est une tentative Google mais que `googleId` est `null` → erreur
  - Si c’est une tentative Email/Password mais que `password` est `null` → erreur

Réponses possibles :
- ✅ `200 OK` → utilisateur trouvé
- 🆕 `404 Not Found` → utilisateur non trouvé → création
- ❌ `409 Conflict` → mauvais mode de connexion

---

### 🔐 3. Si utilisateur trouvé
➡️ Connexion directe :
- Google : redirection vers OAuth → backend échange le code
- Email : appel `POST /auth/login` avec email/mot de passe → création du JWT et cookies

---

### 👶 4. Si utilisateur inconnu
➡️ On propose une création de compte avec confirmation :
- Via modale de confirmation
  Réponses possibles :
  - ✅ Oui -> on redirige vers page de création de compte
  - ❌ Non -> on annule tout et on redirige vers la page de connexion

➡️ Page de création de compte :
- rappel du mail sans modification possible
- input prénom pré-rempli avec info de google si présente
- input nom pré-rempli avec info de google si présente


➡️ Backend : `POST /auth/register`
- Enregistre l’utilisateur avec les bonnes infos
- Vérifie le nombre de groupe auquel appartient l'utilisateur
- Redirige ensuite vers l'onboarding si aucun ou plusieurs groupes ou dashboard si un seul groupe

---

## 🔁 Détail : Email / Mot de passe incorrect
- Si la tentative `POST /auth/login` échoue
- On affiche une modale avec “Mot de passe incorrect”
- Proposer à ce moment-là : “Mot de passe oublié ?”
- Clique → initie le processus de réinitialisation du mot de passe

---

## 🔁 Autres workflows

### 🤕 Mot de passe oublié
- S’affiche uniquement après une erreur de tentative de connexion email/mdp
- Bouton "Mot de passe oublié" dans la modale d’erreur
- Lien vers `/mot-de-passe-oublie`
- Peut déclencher une vérification `check-user` pour confirmer l’existence du compte email/mdp

### 🧰 Réinitialisation du mot de passe
1. L'utilisateur saisit son email sur `/mot-de-passe-oublie`
2. Backend envoie un token temporaire signé par mail
3. L'utilisateur clique → redirigé sur `/reset-password?token=...`
4. Formulaire de changement de mot de passe

---

### ✍️ Changement du mot de passe
Accessible **dans le profil** uniquement pour les utilisateurs qui ont un champ `password` non null :
- Ancien mot de passe
- Nouveau mot de passe (avec regex)
- Confirmation
- Sécurité : envoi d’un mail de confirmation de changement

---
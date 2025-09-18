# Analyse du mode de fonctionnement côté utilisateur - Moments

## Vue d'ensemble

**Moments** est une application Angular 19 de gestion collaborative de cadeaux permettant à des groupes d'utilisateurs de créer, partager et gérer leurs listes de cadeaux. L'application facilite l'organisation des événements (anniversaires, Noël, etc.) en évitant les doublons et en permettant un suivi transparent des achats.

## Architecture générale

### Stack technique frontend
- **Framework** : Angular 19 avec architecture standalone components
- **Routing** : Lazy loading par modules fonctionnels
- **State Management** : Angular Signals pour la réactivité
- **UI/UX** : Thème retro-terminal personnalisé avec responsive design
- **Communication API** : Services HTTP avec gestion d'erreur centralisée

### Patterns architecturaux
- **Service-based architecture** : Logique métier centralisée dans les services
- **Component-based** : Interface modulaire avec composants réutilisables
- **Reactive Programming** : RxJS observables et Angular signals
- **Lazy Loading** : Optimisation des performances par chargement à la demande

---

## Parcours d'authentification et onboarding

### 1. Page d'accueil et connexion
**Localisation** : `welcome.component.ts`

L'application propose deux modes d'authentification :

#### **Connexion Google OAuth2**
- Implémentation PKCE (Proof Key for Code Exchange) pour la sécurité
- Flux : Redirection Google → Code d'autorisation → Exchange backend → JWT tokens
- Gestion "Se souvenir de moi" pour sessions persistantes

#### **Connexion email/mot de passe**
- Validation frontend avec regex (8+ caractères, lettre + chiffre)
- Gestion des erreurs spécifiques :
  - 401 : Mot de passe incorrect (5 tentatives max)
  - 403 : Compte temporairement suspendu
  - 404 : Email inconnu
  - 409 : Compte Google existant sans mot de passe

#### **Inscription par email**
- Vérification d'unicité de l'email
- Envoi d'email de confirmation (30 minutes de validité)
- Finalisation avec définition du profil

### 2. Onboarding nouveaux utilisateurs
**Flux après première connexion** :

1. **Complétion du profil** (`complete-profile.component`)
   - Saisie prénom/nom si non récupérés via Google
   - Validation et sauvegarde du profil utilisateur

2. **Choix du groupe** (`onboarding.component`)
   - **Créer un nouveau groupe** : Définition nom + description
   - **Rejoindre un groupe existant** : Code d'invitation à 6 caractères

3. **Redirection automatique** vers le dashboard du groupe sélectionné

---

## Navigation et structure applicative

### Architecture des routes
**Fichier principal** : `app.routes.ts`

```
/ (racine)           → Page d'accueil/connexion
/auth/*              → Processus d'authentification
/groupe/*            → Gestion et onboarding groupes
/dashboard/*         → Fonctionnalités principales cadeaux
/profile/*           → Gestion profil utilisateur
/compte-tiers/*      → Gestion comptes tiers
/theme               → Personnalisation interface
```

### Modules fonctionnels (lazy-loaded)
- **Auth Module** : Connexion, inscription, réinitialisation mot de passe
- **Groupe Module** : Création, administration, invitation groupes
- **Dashboard Module** : Cœur applicatif de gestion des cadeaux
- **Profile Module** : Paramètres utilisateur et groupes
- **Compte-tiers Module** : Gestion des comptes délégués

---

## Fonctionnalités principales du Dashboard

### 1. Vue d'accueil Dashboard
**Composant** : `dashboard.component.ts`

Interface principale avec navigation contextuelle basée sur :
- **Groupe sélectionné** : Contexte persistant via `GroupContextService`
- **Rôle utilisateur** : Fonctionnalités différenciées ADMIN/MEMBRE
- **Type de compte** : Compte principal ou compte tiers

**Navigation disponible** :
- Mes cadeaux
- Listes des membres
- Suivi des réservations
- Idées cadeaux
- Gestion du groupe (admins uniquement)
- Comptes tiers (fonctionnalité avancée)

### 2. Gestion "Mes cadeaux"
**Route** : `/dashboard/mes-cadeaux`
**Service** : `GiftService`

#### **Liste des cadeaux personnels**
- **Affichage paginé** responsive (limite adaptée mobile/desktop)
- **Réorganisation par priorité** : Système drag & drop intuitif
- **Statuts visuels** : Disponible, Réservé, Pris, Livré
- **Actions rapides** : Modification, suppression, partage

#### **Création/Modification de cadeaux**
**Composants** : `gift-create.component`, `gift-update.component`

**Champs disponibles** :
- Nom du cadeau (obligatoire)
- Description détaillée
- Prix approximatif
- Lien web (suggestion d'achat)
- Priorité dans la liste
- Visibilité (public/privé au groupe)

**Fonctionnalités avancées** :
- **Partage entre membres** : Cadeaux cofinancés
- **Informations de livraison** : Adresse, instructions spéciales
- **Suivi de réception** : Confirmation par le destinataire

### 3. Consultation "Listes des membres"
**Route** : `/dashboard/leurs-cadeaux`

#### **Exploration des listes du groupe**
- **Sélection par membre** : Vue individuelle des listes
- **Filtrage par statut** : Disponibles, déjà réservés
- **Informations contextuelles** : Prix, priorité, description

#### **Système de réservation**
**Workflow** :
1. **Vérification d'éligibilité** (`gift.service.ts:168-182`)
   - Utilisateur ne peut réserver ses propres cadeaux
   - Vérification disponibilité du cadeau
   - Contrôle des permissions groupe

2. **Processus de réservation**
   - Changement statut : Disponible → Réservé
   - **Date d'expiration automatique** (configurable)
   - Notification au destinataire (optionnelle)

3. **Options post-réservation**
   - Ajout informations d'achat
   - Partage avec d'autres membres
   - Gestion de la livraison

### 4. Suivi des réservations
**Route** : `/dashboard/cadeaux-suivis`

#### **Dashboard des achats**
- **Vue consolidée** : Tous les cadeaux réservés par l'utilisateur
- **Informations de suivi** :
  - Date de réservation et expiration
  - Statut d'achat (commandé, livré, remis)
  - Coordonnées de livraison
  - Montant et détails d'achat

#### **Gestion du cycle de vie**
**États possibles** :
- **Réservé** : En attente d'achat
- **Acheté** : Commandé, en cours de livraison
- **Livré** : Prêt à être remis
- **Remis** : Cadeau donné au destinataire
- **Reçu** : Confirmation de réception

### 5. Idées cadeaux
**Route** : `/dashboard/idees`

#### **Système d'inspiration**
- **Capture rapide d'idées** : Formulaire simplifié
- **Conversion en cadeaux** : Transformation idée → cadeau concret
- **Collaboration** : Idées partagées dans le groupe
- **Organisation** : Catégorisation et priorisation

---

## Services et architecture technique

### Services métier principaux

#### **GiftService** (`gift.service.ts`)
**Responsabilités** :
- CRUD complet des cadeaux avec pagination
- Gestion des statuts et transitions
- Système de partage et collaboration
- Vérification d'éligibilité pour actions

**Patterns techniques** :
- **Angular Signals** pour réactivité temps réel
- **Pagination responsive** adaptée au contexte d'affichage
- **Gestion d'erreur centralisée** avec messages utilisateur

#### **GroupService** (`group.service.ts`)
**Responsabilités** :
- Gestion CRUD des groupes
- Système d'invitations avec tokens
- Administration des membres et rôles
- Contexte de groupe persistant

#### **AuthService** (`auth.service.ts`)
**Responsabilités** :
- Authentification OAuth2 et credentials
- Gestion des sessions et tokens JWT
- Switch entre comptes (principal ↔ tiers)
- Profils utilisateur et onboarding

### Architecture des données

#### **Pattern de réactivité**
- **Signals Angular** : État applicatif réactif
- **RxJS Observables** : Communication asynchrone
- **Http Interceptors** : Gestion automatique tokens et erreurs

#### **Gestion d'état**
- **Services stateful** : Données en cache avec signals
- **Context Services** : État partagé (groupe courant, utilisateur)
- **Local Storage** : Persistance préférences utilisateur

---

## Interface utilisateur et composants

### Composants partagés réutilisables

#### **GiftPriorityListComponent**
- **Drag & Drop** : Réorganisation intuitive par glisser-déposer
- **Sauvegarde automatique** : Persistance immédiate des changements
- **Accessibilité** : Support clavier pour utilisateurs sans souris
- **Feedback visuel** : Indication des modifications non sauvegardées

#### **GlobalHeaderContextComponent**
- **Messages contextuels** : Bannières d'information dynamiques
- **Responsive** : Adaptation hauteur selon contenu
- **État réactif** : Mise à jour automatique via signals

#### **Composants de formulaires**
- **GiftFormComponent** : Formulaire cadeaux avec validation
- **TerminalModalComponent** : Modales dans le thème visuel de l'app
- **PaginationComponent** : Navigation paginée responsive

### Thème et design system

#### **Identité visuelle "Retro-Terminal"**
- Police monospace pour l'authenticité
- Palette de couleurs terminaux vintage
- Animations et transitions subtiles
- Iconographie cohérente

#### **Responsive Design**
- **Breakpoints adaptatifs** : Mobile-first approach
- **Navigation simplifiée** mobile : Menu hamburger, actions rapides
- **Pagination intelligente** : Moins d'éléments sur petit écran
- **Touch-friendly** : Zones de clic adaptées tactile

---

## Fonctionnalités avancées

### 1. Gestion des comptes tiers
**Route** : `/dashboard/comptes-tiers`

#### **Concept des comptes délégués**
Les comptes tiers permettent de gérer des listes de cadeaux pour des personnes qui ne peuvent ou ne souhaitent pas utiliser l'application directement :
- **Adultes peu technophiles** : Personnes âgées, utilisateurs réfractaires au numérique
- **Personnes à mobilité réduite** : Difficultés d'accès aux interfaces numériques
- **Utilisateurs occasionnels** : Participation ponctuelle aux événements du groupe
- **Contextes familiaux** : Parents gérant les listes d'enfants multiples

#### **Fonctionnalités de délégation**
- **Création de comptes tiers** : Profils gérés par le compte principal
- **Switch de contexte** (`auth.service.ts:296-324`) : Basculement entre identités
- **Gestion des permissions** : Actions autorisées pour chaque compte tiers
- **Synchronisation** : Cohérence des données entre comptes

### 2. Système de partage et collaboration

#### **Partage de cadeaux**
- **Cofinancement** : Plusieurs membres participent à un même cadeau
- **Coordination** : Communication entre contributeurs
- **Transparence** : Suivi des participations de chacun

#### **Gestion des groupes**
**Fonctionnalités administrateur** :
- **Invitations par email** : Envoi automatique avec tokens uniques
- **Gestion des rôles** : Promotion/rétrogradation MEMBRE ↔ ADMIN
- **Modération** : Exclusion de membres, gestion des conflits
- **Paramétrage** : Configuration des règles du groupe

### 3. Notifications et communication

#### **Système de messaging intégré**
- **Notifications contextuelles** : Bannières d'information en temps réel
- **Toastr messages** : Confirmations et alertes d'actions
- **Emails automatiques** : Invitations, rappels, confirmations

#### **Feedback utilisateur**
- **Messages d'erreur explicites** : Guidance pour résolution de problèmes
- **Confirmations visuelles** : Validation des actions importantes
- **États de chargement** : Indicateurs de progression pour actions longues

---

## Flux utilisateur types

### Scénario 1 : Nouveau membre rejoint un groupe
1. **Réception invitation** (email avec code à 6 caractères)
2. **Création compte** via lien ou saisie manuelle du code
3. **Complétion profil** si nécessaire
4. **Accès automatique** au dashboard du groupe
5. **Découverte interface** avec assistance contextuelle

### Scénario 2 : Préparation d'un événement
1. **Création/mise à jour liste personnelle** de cadeaux souhaités
2. **Priorisation** par drag & drop selon préférences
3. **Consultation des listes** des autres membres
4. **Réservations stratégiques** en évitant les doublons
5. **Suivi des achats** jusqu'à la remise des cadeaux

### Scénario 3 : Administration d'un groupe familial
1. **Configuration du groupe** : nom, description, règles
2. **Invitation des membres** par email ou partage de code
3. **Gestion des comptes tiers** pour membres non autonomes
4. **Modération** : résolution conflits, ajustement permissions
5. **Coordination événements** : rappels, deadlines, organisation

---

## Points d'attention et bonnes pratiques

### Sécurité et confidentialité
- **Authentification robuste** : OAuth2 + JWT avec refresh tokens
- **Permissions granulaires** : Accès limité selon rôle et contexte
- **Données sensibles** : Chiffrement des informations personnelles
- **Sessions sécurisées** : Expiration automatique, logout propre

### Performance et scalabilité
- **Lazy loading** : Chargement différé des modules
- **Pagination adaptative** : Gestion efficace de grandes listes
- **Cache intelligent** : Réduction des appels API redondants
- **Optimisation mobile** : Bundle size et temps de chargement réduits

### Accessibilité et inclusion
- **Support clavier** : Navigation complète sans souris
- **Contrastes suffisants** : Lisibilité pour malvoyants
- **Messages explicites** : Guidance claire pour tous niveaux
- **Responsive design** : Adaptation tous supports et tailles d'écran

---

## Conclusion

Moments offre une **expérience utilisateur collaborative fluide** centrée sur la **simplicité d'usage** et la **coordination de groupe**. L'architecture technique moderne garantit **performance**, **sécurité** et **évolutivité**, tandis que le design soigné assure une **adoption facile** par des utilisateurs de tous niveaux techniques.

L'application excelle particulièrement dans :
- La **gestion intuitive** des listes de cadeaux
- La **coordination transparente** entre membres d'un groupe
- L'**inclusion** via les comptes tiers pour utilisateurs moins autonomes
- L'**expérience mobile** optimisée pour usage nomade

Ces caractéristiques en font un outil de choix pour **organiser sereinement** les événements familiaux et amicaux, en **évitant les doublons** et en **facilitant la surprise** pour tous les participants.
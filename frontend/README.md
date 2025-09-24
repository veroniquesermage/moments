# 🎨 Moments Frontend - Angular Application

Frontend de l'application Moments, développé avec Angular 19 et TypeScript, offrant une interface moderne et réactive pour la gestion de cadeaux en groupe.

## 🛠️ Technologies

- **Angular 19** - Framework SPA avec les dernières fonctionnalités
- **TypeScript 5+** - Typage statique et features ES2022+
- **SCSS** - Préprocesseur CSS avec architecture modulaire
- **Angular Signals** - Gestion d'état
- **Angular Router** - Navigation avec lazy loading
- **Angular Forms** - Formulaires réactifs avec validation
- **HttpClient** - Communication API avec interceptors

## 🚀 Installation et Développement

### Prérequis
- **Node.js 18+**
- **npm** ou **yarn**
- **Angular CLI** (optionnel mais recommandé)

## 🏗️ Architecture

### Patterns architecturaux

#### 🔄 Architecture basée sur les Services
- **Services centralisés** : Chaque domaine métier a son service dédié
- **Injection de dépendances** : Utilisation du système DI d'Angular
- **Angular Signals** : Gestion d'état réactive

#### 🛣️ Routing et Navigation
- **Lazy Loading** : Chargement différé des modules pour optimiser les performances
- **Route Guards** : Protection des routes sensibles
- **Route Parameters** : Gestion des paramètres dynamiques

#### 📝 Formulaires et Validation
- **Reactive Forms** : Formulaires pilotés par le modèle
- **Validation custom** : Validateurs personnalisés pour les règles métier
- **Error Handling** : Gestion centralisée des erreurs de validation

## 🎨 Interface Utilisateur

### Thème et Design
- **Thème rétro-terminal** : Design inspiré des terminaux vintage
- **Responsive Design** : Adaptation mobile et desktop
- **Accessibilité** : Respect des standards WCAG

## 📱 Fonctionnalités

### ✨ Fonctionnalités principales
- **Dashboard interactif** avec vue d'ensemble des cadeaux
- **Gestion complète des listes** de souhaits
- **Système de réservation** avec dates d'expiration
- **Partage de cadeaux** entre membres

### 🚀 Optimisations
- **Lazy Loading** : Chargement des modules à la demande
- **OnPush Strategy** : Optimisation des cycles de détection
- **TrackBy Functions** : Optimisation des listes *ngFor

## 🔒 Sécurité

### Authentification
- **JWT Tokens** : Stockage sécurisé et rotation automatique
- **Route Guards** : Protection des routes par authentification
- **HTTP Interceptors** : Injection automatique des tokens

### Validation et Sanitization
- **Input Validation** : Validation côté client et serveur
- **XSS Protection** : Sanitization automatique des inputs

## 📚 Ressources

- [Angular Documentation](https://angular.io/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Angular Signals Guide](https://angular.io/guide/signals)
- [Angular Material](https://material.angular.io/) (si utilisé)

---

*Interface moderne et performante pour une expérience utilisateur optimale en gestion de cadeaux* 🎁✨

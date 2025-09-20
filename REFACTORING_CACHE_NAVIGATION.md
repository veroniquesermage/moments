# 🔧 Plan de Refactoring : Cache et Navigation

**Objectif :** Résoudre tous les problèmes de cache, persistance et navigation dans l'application Angular.

**Durée estimée :** 1-2 semaines
**Approche :** Étape par étape avec validation à chaque niveau

---

## 📋 Plan d'Action Détaillé

### 🎯 **ÉTAPE 1 : Service de Persistance Centralisé** *(Priorité 1)*
**Durée :** 1-2 jours
**Objectif :** Centraliser toute la logique de sauvegarde/restauration des données

#### 1.1 Créer le PersistenceService
- [ ] Créer `src/core/services/persistence.service.ts`
- [ ] **Stratégie MINIMAL Storage :**
  - **localStorage** : GroupId actif, Préférences utilisateur (thème)
  - **sessionStorage** : État navigation UNIQUEMENT (position, filtres, scroll)
  - **Cookies httpOnly** : Tokens (access/refresh) - PAS TOUCHER (sécurisé)
  - **Signaux** : Single Source of Truth (données toujours fresh)
  - **JAMAIS** : Cache des cadeaux/membres (toujours fetch)
- [ ] Implémenter les méthodes de base (save, restore, clear)
- [ ] Gérer la synchronisation automatique (pas de sync manuelle)
- [ ] Ajouter la gestion des TTL (Time To Live)

#### 1.2 Intégrer dans les services existants
- [ ] Modifier `AuthService` pour utiliser PersistenceService
- [ ] Modifier `GroupContextService` pour utiliser PersistenceService
- [ ] Modifier `GroupService` pour utiliser PersistenceService
- [ ] Modifier `ThemeService` pour utiliser PersistenceService

#### 1.3 Tests et validation
- [ ] Tester F5 : toutes les données reviennent
- [ ] Tester logout : tout est nettoyé
- [ ] Tester changement de groupe : pas de mélange de données

---

### 🎯 **ÉTAPE 2 : Service de Cache de Navigation MINIMAL** *(Priorité 1)*
**Durée :** 0.5-1 jour (simplifié !)
**Objectif :** Conserver UNIQUEMENT l'état de navigation (position, filtres, scroll)

#### 2.1 Créer le NavigationStateService (simple)
- [ ] Créer `src/core/services/navigation-state.service.ts`
- [ ] **Cache UNIQUEMENT :**
  - Position dans les listes (page courante, filtres, tri)
  - Position de scroll
  - État des formulaires (brouillons)
- [ ] **PAS de cache pour :**
  - Cadeaux (toujours fresh)
  - Membres (toujours fresh)
  - Données business critiques
- [ ] Utiliser sessionStorage (expire avec l'onglet)

#### 2.2 Intégrer dans les composants de liste
- [ ] Modifier `UserGiftsComponent` (position/filtres seulement)
- [ ] Modifier `GroupMemberGiftsComponent` (position/filtres seulement)
- [ ] Modifier `MyGiftsFollowUpComponent` (position/filtres seulement)
- [ ] Les données sont TOUJOURS fetchées (fresh)

#### 2.3 Tests et validation
- [ ] Navigation vers détail → retour : position conservée, données fresh
- [ ] Page 3 → détail → retour : toujours page 3 mais données rechargées
- [ ] Filtres appliqués → navigation → retour : filtres conservés
- [ ] F5 : position perdue (normal) mais données fraîches

---

### 🎯 **ÉTAPE 3 : Amélioration du Cycle de Vie d'Application** *(Priorité 2)*
**Durée :** 1 jour
**Objectif :** Garantir un ordre d'initialisation correct

#### 3.1 Refactoriser le StartupService
- [ ] Améliorer `src/core/services/startup.service.ts`
- [ ] Implémenter une séquence d'initialisation robuste
- [ ] Ajouter la validation de cohérence des données
- [ ] Gérer les cas d'erreur et de récupération

#### 3.2 Modifier AppComponent
- [ ] Simplifier les effects dans `app.component.ts`
- [ ] Déléguer l'initialisation au StartupService
- [ ] Améliorer la gestion des états de chargement

#### 3.3 Tests et validation
- [ ] F5 : initialisation dans le bon ordre
- [ ] Pas de flash de déconnexion
- [ ] Redirection correcte selon l'état utilisateur

---

### 🎯 **ÉTAPE 4 : Service de Gestion d'Invitations** *(Priorité 2)*
**Durée :** 0.5-1 jour
**Objectif :** Résoudre les race conditions des invitations

#### 4.1 Créer InvitationService
- [ ] Créer `src/core/services/invitation.service.ts`
- [ ] Centraliser la logique de gestion des tokens d'invitation
- [ ] Éliminer les race conditions
- [ ] Gérer les différents scenarios (connecté/déconnecté)

#### 4.2 Refactoriser les composants
- [ ] Modifier `GroupJoinComponent`
- [ ] Modifier `AppComponent` (logic d'invitation)
- [ ] Nettoyer la logique dispersée

#### 4.3 Tests et validation
- [ ] Invitation utilisateur connecté : fonctionne
- [ ] Invitation utilisateur déconnecté : fonctionne
- [ ] Pas de token perdu en cours de route

---

### 🎯 **ÉTAPE 5 : Nettoyage et Logout Robuste** *(Priorité 1)*
**Durée :** 0.5 jour
**Objectif :** Déconnexion propre sans fuite de données

#### 5.1 Améliorer la méthode logout
- [ ] Utiliser PersistenceService pour nettoyage total
- [ ] Nettoyer tous les signaux de tous les services
- [ ] Vider le cache de navigation
- [ ] Gérer les cas d'erreur de logout

#### 5.2 Tests et validation
- [ ] Logout → plus aucune donnée de l'utilisateur précédent
- [ ] Logout → nouveau login fonctionne parfaitement
- [ ] Logout → pas de mélange entre utilisateurs

---

### 🎯 **ÉTAPE 6 : Gestion Robuste des Changements de Groupe** *(Priorité 1)*
**Durée :** 0.5-1 jour
**Objectif :** Changement de groupe sans mélange de données

#### 6.1 Améliorer setGroupContext
- [ ] Nettoyer les données de l'ancien groupe
- [ ] Charger les données du nouveau groupe
- [ ] Notifier tous les services du changement
- [ ] Invalider les caches pertinents

#### 6.2 Tests et validation
- [ ] Changement Groupe A → Groupe B : pas de mélange
- [ ] Listes rechargées correctement
- [ ] Pas de données fantômes

---

### 🎯 **ÉTAPE 7 : Amélioration des Signaux Réactifs** *(Priorité 3)*
**Durée :** 0.5 jour
**Objectif :** Tous les signaux sont réactifs et cohérents

#### 7.1 Convertir les services restants
- [ ] Convertir `ThemeService.current` en signal
- [ ] Améliorer `ResponsiveService` avec persistance
- [ ] Vérifier la cohérence de tous les signaux

#### 7.2 Tests et validation
- [ ] Tous les changements d'état sont réactifs
- [ ] Interface met à jour automatiquement
- [ ] Pas de lag ou d'incohérence

---

## 🧪 **ÉTAPE 8 : Tests et Validation Globale** *(Obligatoire)*
**Durée :** 1 jour

### 8.1 Scénarios de test complets
- [ ] **Test F5** : Toutes les pages, toutes les données reviennent
- [ ] **Test Navigation** : Aller-retour conserve les états
- [ ] **Test Multi-onglets** : Cohérence entre onglets
- [ ] **Test Logout/Login** : Nettoyage complet
- [ ] **Test Invitation** : Tous les flows d'invitation
- [ ] **Test Changement Groupe** : Pas de mélange

### 8.2 Tests de performance
- [ ] Temps de chargement initial acceptable
- [ ] Pas de lag lors des changements d'état
- [ ] Mémoire : pas de fuites

### 8.3 Tests edge cases
- [ ] Connexion internet coupée
- [ ] Token expiré pendant navigation
- [ ] Données corrompues dans localStorage

---

## 📦 **Livrables par Étape**

### Étape 1 ✅
- `persistence.service.ts` avec **MINIMAL Storage**
  - localStorage pour données persistantes (groupId, thème)
  - sessionStorage pour état navigation UNIQUEMENT (position, filtres)
  - Cookies httpOnly pour tokens (PAS TOUCHER - déjà sécurisé)
  - Signaux comme Single Source of Truth (données toujours fresh)
- Services modifiés (Auth, GroupContext, Group, Theme)
- Tests de validation F5/Logout

### Étape 2 ✅
- `navigation-state.service.ts` (simplifié !)
- Composants de liste modifiés (position/filtres seulement)
- Données TOUJOURS fetchées (fresh)
- Tests de navigation

### Étape 3 ✅
- `startup.service.ts` amélioré
- `app.component.ts` simplifié
- Tests d'initialisation

### Étape 4 ✅
- `invitation.service.ts`
- Composants d'invitation refactorisés
- Tests de flow d'invitation

### Étape 5 ✅
- Logout robuste
- Tests de déconnexion

### Étape 6 ✅
- Changement de groupe propre
- Tests de changement de contexte

### Étape 7 ✅
- Signaux cohérents
- Tests de réactivité

### Étape 8 ✅
- Application complètement testée
- Documentation des améliorations

---

## 🎯 **Critères de Succès**

### ✅ **Après Étape 1-2 (Critique)**
- F5 ne fait plus perdre de données
- Navigation arrière conserve les états
- Logout nettoie tout

### ✅ **Après Étape 3-4 (Important)**
- Initialisation robuste
- Invitations sans bug
- Performance acceptable

### ✅ **Après Étape 5-6 (Final)**
- Changement de groupe propre
- Aucune fuite de données
- UX fluide et cohérente

### ✅ **Après Étape 7-8 (Polish)**
- Application production-ready
- Tous les edge cases gérés
- Code maintenable

---

## 📝 **Notes de Progression**

**Date de début :** _À remplir_
**Étape actuelle :** Étape 1 - Préparation
**Blockers :** _Aucun actuellement_
**Prochaine validation :** Étape 1.1 - PersistenceService

---

## 🏗️ **Architecture de Stockage Décidée**

### ✅ **Hybrid MINIMAL Storage Strategy**
- **localStorage** ← Données persistantes (groupId actif, préférences utilisateur)
- **sessionStorage** ← État de navigation UNIQUEMENT (position, filtres, scroll)
- **Cookies httpOnly** ← Tokens (access_token, refresh_token) - SÉCURISÉ
- **Signaux Angular** ← Single Source of Truth (état réactif temps réel)
- **JAMAIS de cache** ← Cadeaux, membres, données business (toujours fresh)

### 💡 **Principes MINIMALISTES Retenus**
1. **Cache QUE l'état UI** : Position, filtres, scroll - PAS les données business
2. **Données toujours fresh** : Cadeaux et membres TOUJOURS fetchés
3. **Signaux = source unique** : localStorage/sessionStorage = état UI seulement
4. **Simple = robuste** : Moins de cache = moins de bugs de sync
5. **UX fluide** : Navigation conserve la position, données restent fraîches

---

**🚀 Prêt à commencer par l'Étape 1.1 : Création du PersistenceService avec approche MINIMALISTE ?**

---

## 🎯 **Résumé de l'Approche MINIMALISTE**

### ✅ **Ce qu'on cache :**
- Position dans les listes (page courante)
- Filtres appliqués
- Position de scroll
- Préférences utilisateur (thème)
- GroupId actif

### ❌ **Ce qu'on ne cache JAMAIS :**
- Cadeaux (toujours fresh)
- Membres du groupe (toujours fresh)
- Statuts business (toujours fresh)
- Données critiques

### 🏆 **Bénéfices :**
- **UX fluide** : Navigation retour conserve l'état
- **Données fraîches** : Ed apparaîtra dès que Caro refresh
- **Simple** : Pas de logique complexe de cache
- **Robuste** : Moins de bugs de synchronisation
#!/bin/bash

# Script de nettoyage Docker pour Moments
# Nettoie les ressources Docker inutilisées pour libérer de l'espace

echo "🐳 Démarrage du nettoyage Docker..."

# Afficher l'espace avant nettoyage
echo "📊 Espace Docker avant nettoyage :"
docker system df

echo ""
echo "🧹 Nettoyage en cours..."

# Nettoyer les containers arrêtés
echo "  - Suppression des containers arrêtés..."
docker container prune -f

# Nettoyer les réseaux non utilisés
echo "  - Suppression des réseaux non utilisés..."
docker network prune -f

# Nettoyer les volumes non utilisés (ATTENTION: garde les volumes nommés)
echo "  - Suppression des volumes anonymes non utilisés..."
docker volume prune -f

# Nettoyer les images non utilisées (sauf celles taguées)
echo "  - Suppression des images non utilisées..."
docker image prune -f

# Nettoyer le cache de build (libère beaucoup d'espace)
echo "  - Suppression du cache de build..."
docker builder prune -f

echo ""
echo "📊 Espace Docker après nettoyage :"
docker system df

# Calculer l'espace libéré
echo ""
echo "✅ Nettoyage Docker terminé"

# Log du nettoyage
LOG_DIR="/app/logs"
if [ -d "$LOG_DIR" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Nettoyage Docker effectué" >> "$LOG_DIR/cleanup.log"
fi
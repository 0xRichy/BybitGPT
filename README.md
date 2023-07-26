# BybitGPT - Bot de Trading Automatique avec ChatGPT et Notifications Telegram

BybitGPT est un bot de trading automatique qui utilise l'IA ChatGPT pour prendre des décisions de trading en temps réel. Le bot est conçu pour prendre des décisions d'achat ou de vente de Bitcoin (BTC) en fonction des conditions actuelles du marché, telles que déterminées par le modèle ChatGPT de OpenAI.

Le bot effectue automatiquement des transactions en fonction des réponses fournies par ChatGPT et envoie des notifications en temps réel sur Telegram pour vous tenir informé des actions prises.

## Configuration requise

- Python 3.x installé sur votre système.
- Clés d'API Bybit pour l'accès au compte de trading.
- Clé d'API OpenAI pour l'utilisation du modèle ChatGPT.
- Token de bot Telegram pour envoyer des notifications.
- ID du chat Telegram où vous souhaitez recevoir les notifications.

## Installation

1. Clonez ce référentiel sur votre machine locale ou sur votre VPS :

```
git clone https://github.com/votre_utilisateur/BybitGPT.git
```

2. Accédez au répertoire du projet :

```
cd BybitGPT
```

3. Installez les dépendances requises en exécutant la commande suivante :

```
pip install -r requirements.txt
```

4. Configurer les clés d'API et les paramètres du bot :

   - Ouvrez le fichier `.env` dans un éditeur de texte.
   - Remplacez les valeurs `your_api_key`, `your_secret_key`, `your_openai_api_key`, `your_bot_token`, et `your_chat_id` par vos propres clés et paramètres. Enregistrez le fichier.

## Utilisation

Pour lancer le bot BybitGPT, exécutez la commande suivante :

```
python bot_trading.py
```

Le bot commencera à prendre des décisions de trading en fonction des réponses fournies par ChatGPT et effectuera des transactions automatiques en temps réel. Les notifications concernant les actions du bot seront envoyées sur le chat Telegram spécifié.

## Notes

- Assurez-vous que votre bot de trading est configuré avec soin pour éviter tout comportement imprévu et des pertes financières.
- Ce projet est destiné à des fins éducatives et d'apprentissage. N'utilisez pas de vrais fonds tant que vous n'avez pas testé le bot et compris son fonctionnement.
- Les clés d'API et les informations sensibles doivent être gardées confidentielles et ne doivent pas être partagées publiquement.

Amusez-vous bien avec BybitGPT, votre bot de trading automatisé !

---

N'hésitez pas à personnaliser davantage le contenu si nécessaire pour mieux refléter les spécificités de votre projet. Le fichier `README.md` est une ressource précieuse pour les utilisateurs, alors assurez-vous d'y inclure toutes les informations importantes pour les aider à installer, configurer et utiliser le bot en toute sécurité.

Si vous avez des questions supplémentaires ou avez besoin de plus d'aide, n'hésitez pas à demander ! Bonne utilisation de BybitGPT et bon trading !

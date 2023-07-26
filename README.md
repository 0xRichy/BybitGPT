# BybitGPT - Bot de Trading Automatique avec ChatGPT et Notifications Telegram

BybitGPT est un bot de trading automatique qui utilise l'IA ChatGPT pour prendre des décisions de trading en temps réel. Le bot est conçu pour prendre des décisions d'achat ou de vente de Bitcoin (BTC) en fonction des conditions actuelles du marché, telles que déterminées par le modèle ChatGPT de OpenAI.

Le bot effectue automatiquement des transactions en fonction des réponses fournies par ChatGPT et envoie des notifications en temps réel sur Telegram pour vous tenir informé des actions prises. De plus, le bot offre une interface de commande sur Telegram pour interagir avec le bot et obtenir des informations sur le compte de trading.

## Configuration requise

- Python 3.x installé sur votre système.
- Clés d'API Bybit pour l'accès au compte de trading.
- Clé d'API OpenAI pour l'utilisation du modèle ChatGPT.
- Token de bot Telegram pour envoyer des notifications.
- ID du chat Telegram où vous souhaitez recevoir les notifications.

## Installation

1. Clonez ce référentiel sur votre machine locale ou sur votre VPS :

```
git clone https://github.com/0xRichy/BybitGPT.git
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

   - Ouvrez le fichier `BybitGPT.py` dans un éditeur de texte.
   - Remplacez les valeurs `'YOUR_BYBIT_API_KEY'`, `'YOUR_BYBIT_SECRET'`, `'YOUR_OPENAI_API_KEY'`, `'YOUR_TELEGRAM_BOT_TOKEN'`, et `'YOUR_TELEGRAM_CHAT_ID'` par vos propres clés et paramètres. Enregistrez le fichier.

## Utilisation

Pour lancer le bot BybitGPT, exécutez la commande suivante :

```
python BybitGPT.py
```

Le bot commencera à prendre des décisions de trading en fonction des réponses fournies par ChatGPT et effectuera des transactions automatiques en temps réel. Les notifications concernant les actions du bot seront envoyées sur le chat Telegram spécifié.

## Commandes Telegram

Le bot offre les commandes suivantes sur Telegram :

- `/balance` - Obtenir votre balance actuelle.
- `/trades` - Obtenir vos trades en cours.
- `/restart` - Redémarrer le bot.
- `/set_leverage` - Définir le levier (Exemple : `/set_leverage 10`).
- `/help` - Obtenir la liste des commandes disponibles.

## Notes

- Assurez-vous que votre bot de trading est configuré avec soin pour éviter tout comportement imprévu et des pertes financières.
- Ce projet est destiné à des fins éducatives et d'apprentissage. N'utilisez pas de vrais fonds tant que vous n'avez pas testé le bot et compris son fonctionnement.
- Les clés d'API et les informations sensibles doivent être gardées confidentielles et ne doivent pas être partagées publiquement.

Amusez-vous bien avec BybitGPT, votre bot de trading automatisé !


N'oubliez pas de remplacer `'YOUR_BYBIT_API_KEY'`, `'YOUR_BYBIT_SECRET'`, `'YOUR_OPENAI_API_KEY'`, `'YOUR_TELEGRAM_BOT_TOKEN'` et `'YOUR_TELEGRAM_CHAT_ID'` par vos propres clés API et identifiants.

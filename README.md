# SARLAT CHEZ BAPTISTE

Fiche publique DIGIYLYFE pour une **chambre privée chez l’habitant à Sarlat-la-Canéda**.

La page assume clairement la réalité de l’adresse :

- Baptiste vit dans le logement ;
- le voyageur dispose de son espace privé ;
- la présence de l’hôte reste discrète ;
- la cuisine est accessible et partagée avec l’hôte ;
- il ne s’agit ni d’un hôtel ni d’un appartement vide.

## Fichiers du dépôt

```text
index.html
README.md
photos/
  cover.jpg
  chambre.jpg
  lit.jpg
  salle-de-bain.jpg
  cuisine.jpg
  ambiance.jpg
```

Les photos ne sont pas incluses dans ce paquet afin de ne pas utiliser d’images génériques ou trompeuses.  
Exportez les **photos réelles** de votre annonce et renommez-les exactement comme ci-dessus.

Même sans photos, la page reste lisible : des cadres de remplacement sont affichés automatiquement.

## Mise en ligne sur GitHub Pages

1. Créez un dépôt public, par exemple :

```text
sarlat-chez-baptiste
```

2. Déposez `index.html`, `README.md` et le dossier `photos`.

3. Ouvrez :

```text
Settings → Pages
```

4. Choisissez :

```text
Deploy from a branch
Branch: main
Folder: / (root)
```

5. Enregistrez.

GitHub fournit ensuite une adresse de type :

```text
https://beauville.github.io/sarlat-chez-baptiste/
```

## Domaine DIGIYLYFE conseillé

Domaine prévu dans le fichier :

```text
https://sarlat-chez-baptiste.digiylyfe.com/
```

Pour l’utiliser, créez à la racine un fichier nommé `CNAME` contenant uniquement :

```text
sarlat-chez-baptiste.digiylyfe.com
```

Puis ajoutez le sous-domaine dans votre zone DNS selon votre configuration GitHub Pages habituelle.

Si vous choisissez un autre domaine, remplacez dans `index.html` :

```text
https://sarlat-chez-baptiste.digiylyfe.com/
```

dans :

- la balise `canonical` ;
- les balises Open Graph ;
- le JSON-LD ;
- `CONFIG.siteUrl`.

## Configuration des boutons

Dans `index.html`, recherchez :

```js
const CONFIG = {
```

Le lien Booking est déjà renseigné.

Ajoutez les numéros au format international :

```js
phone: "+33600000000",
whatsapp: "33600000000",
```

Tant que ces champs restent vides, les boutons **Appeler** et **WhatsApp** sont automatiquement masqués.  
Aucun faux contact n’est affiché.

## Bouton Booking

Lien actuellement configuré :

```text
https://www.booking.com/hotel/fr/chez-baptiste.fr.html
```

Booking reste utilisé pour :

- les disponibilités ;
- les tarifs ;
- les conditions ;
- la réservation.

La fiche DIGIYLYFE conserve :

- l’identité de SARLAT CHEZ BAPTISTE ;
- la présentation humaine ;
- les photos réelles ;
- le QR personnel ;
- la route vers la page territoriale SARLAT.

## Informations affichées

La page présente notamment :

- 3 rue du Troubadour Cairels, 24200 Sarlat-la-Canéda ;
- capacité de 2 voyageurs ;
- grand lit ;
- salle de bain privative avec baignoire ;
- cuisine accessible et partagée avec l’hôte ;
- Wi-Fi ;
- télévision ;
- lave-linge ;
- coin repas ;
- arrivée de 15 h à 22 h ;
- départ de 8 h à 10 h ;
- logement non-fumeur ;
- accès aux étages par les escaliers.

Avant publication définitive, vérifiez que chaque information correspond toujours à l’annonce active.

## Architecture DIGIYLYFE

Parcours recommandé :

```text
DIGIYLYFE
→ Page territoriale SARLAT
→ SARLAT CHEZ BAPTISTE
→ Booking pour les dates et la réservation
```

Doctrine :

```text
Le premier client peut venir d’une plateforme.
La relation et l’identité restent au professionnel.
```

---

**DIGIYLYFE — Le terrain garde la main.**

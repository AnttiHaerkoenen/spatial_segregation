% Spatiaalinen segregaatioanalyysi ja autonomian ajan lopun uskonnolliset ryhmät
% Antti Härkönen
% 2019-10-25

# Taustaa

## Viipuri

- ruotsalainen linna vesireittien hallitsemiseen
- kaupunkioikeudet 1403

## Venäjän aika

- venäläiset valtasivat 1710
- suuri venäläinen varuskunta
- Viipurin kuvernementti liitettiin Suomen suuriruhtinaskuntaan 1812

## 1800-luku

- teollistuminen
- Saimaan kanva 1856
- Pietari-Helsinki rata 1870

## Luterilaiset

- alemmat yhteiskuntaluokat suomenkielisiä
- ruotsin- ja saksankieliset vähemmistöt

## Ortodoksit

- Venäjältä muuttaneita
- venäjänkielisiä

## 1900-luvun alku

- venäläistämistoimet vaikuttivat Viipurin läänissä eniten
- poliittinen jännitys

## Sisällissota

- ensimmäinen yhteenotto Viipurissa 19.1. 
- kaupunki punaisten hallussa melkein koko sodan

## Viipurin valtaus

- valkoiset ampuivat valtauksen jälkeen paitsi punaisia myös venäjänkielistä siviiliväestöä

# Tutkimusongelma

## Kysymykset

- kuinka segregaatio muuttui vuosien varrella
- ortodoksit vs valtaväestö

# Aineisto & Menetelmät

## Aineisto

- henkikirjat
- katasterikartat

## Konenäkö

- scikit-image (Python)
- kuvan puhdistaminen
- numeroiden erottaminen
- koulutusaineiston tuottaminen

## Koneoppiminen

- ohjattu syväoppiminen
- hermoverkkomalli
- lupaavia tuloksia numeroiden tunnistamisessa
- vaatii runsaasti koulutusdataa

## Segregaatioanalyysi

- spatiaalinen segregaatioanalyysi
- perinteiset aspatiaaliset indeksit (esim. Index of dissimilarity) kärsivät MAUPista

## Ydinestimointi

- ydinestimointi (Kernel Density Estimation, KDE)
- rasteri kuvaa väestön jakautumista kaupunkitilassa

<section>
<figure></figure>
</section>

## Spatiaalinen segregaatioindeksi S

- $S = 1 - \frac{V_{\cap}}{V_{\cup}}$
- $$V_{\cap} = \sum_{n=0}^N{min(\tilde p_{hn}, \tilde p_{gn})}$$
- $$V_{\cup} = \sum_{n=0}^N{max(\tilde p_{hn}, \tilde p_{gn})}$$

# Tuloksia

## Segregaatio

- S:n arvo laskee 1880-1900 ja nousee 1900-1920
- ortodoksien asuinalueet vaihtuvat huomattavasti

## Mitä nyt

- lisää aineistoa käyttöön
- koneoppimista parannettava
- [github.com/AnttiHaerkoenen](https://www.github.com/AnttiHaerkoenen)

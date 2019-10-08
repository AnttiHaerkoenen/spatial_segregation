% Spatiaalinen segregaatioanalyysi ja autonomian ajan lopun uskonnolliset ryhmät
% Antti Härkönen
% 2019-10-25

# Taustaa

# Viipuri

- ruotsalainen linna vesireittien hallitsemiseen
- kaupunkioikeudet 1403

# Venäjän aika

- venäläiset valtasivat 1710
- suuri venäläinen varuskunta
- Viipurin kuvernementti liitettiin Suomen suuriruhtinaskuntaan 1812

# 1800-luku

- teollistuminen
- Saimaan kanva 1856
- Pietari-Helsinki rata 1870

# Luterilaiset

- alemmat yhteiskuntaluokat suomenkielisiä
- ruotsin- ja saksankieliset vähemmistöt

# Ortodoksit

- Venäjältä muuttaneita
- venäjänkielisiä

# 1900-luvun alku

- venäläistämistoimet vaikuttivat Viipurin läänissä eniten
- poliittinen jännitys

# Itsenäistyminen ja sisällissota

- ensimmäinen yhteenotto Viipurissa 19.1. 
- kaupunki punaisten hallussa melkein koko sodan
- valkoiset ampuivat valtauksen jälkeen paitsi punaisia myös venäjänkielistä siviiliväestöä

# Tutkimusongelma

- kuinka segregaatio muuttui vuosien varrella
- ortodoksit vs valtaväestö

# todo todo

# Data & Methods

# Data

- population & tax registers
- cadastral maps
- handwritten digit recognition using CV & ML

# Methods

- spatial segregation analysis
- traditional aspatial indices (e.g. Index of dissimilarity) suffer from MAUP

# Kernel density estimation

- smoothing of population surfaces using kernel functions
- grid represents continuous distribution of population in town space

# Spatial segregation index S

- $S = 1 - \frac{V_{\cap}}{V_{\cup}}$
- $$V_{\cap} = \sum_{n=0}^N{min(\tilde p_{hn}, \tilde p_{gn})}$$
- $$V_{\cup} = \sum_{n=0}^N{max(\tilde p_{hn}, \tilde p_{gn})}$$

# Results

# Segregation

- S seems to first decrease, then increase
- concentrations of Orthodox population change significantly

# Conclusion

- integration in peaceful times 
- ... followed by segregation and violence during political crisis

# What next

- more data needed
- software for automatic reading of sources coming along
- [github.com/AnttiHaerkoenen](https://www.github.com/AnttiHaerkoenen)

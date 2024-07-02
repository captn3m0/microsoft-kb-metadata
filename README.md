# Microsoft Knowledge Base metadata

This repository hosts a small subset of the Microsoft Knowledgebase metadata. The data in the `data.json` contains the following:

1. Date of the KB publication
2. KB UUID
3. KB Slug
4. KB URL

The list of KB IDs in the database is scraped from the URLs in `discovery.txt`. The primary usecase of the dataset is to provide a `KB:DATE`
mapping to other projects.

## wip

Discovery notes. Need to check the sitemaps more thoroughly before i automate this

See https://learn.microsoft.com/_sitemaps/sitemapindex.xml

```
curl --silent https://learn.microsoft.com/_sitemaps/officeupdates_en-us_1.xml | yq -p xml -o c '.urlset.url[]|.loc' >> discovery.txt
curl --silent https://learn.microsoft.com/_sitemaps/security-updates_en-us_1.xml | yq -p xml -o c '.urlset.url[]|.loc' >> discovery.txt
```

## license

Data and code in this repository is licensed under [Creative Commons Zero v1.0 Universal](https://choosealicense.com/licenses/cc0-1.0/).
# Wikipedia Edit Wars
This project uses a Naive Bayes model to predict what Wikipedia articles are likely to be the subject of an edit war.

[What is an edit war?](https://en.wikipedia.org/wiki/Wikipedia:Edit_warring)

This project uses the Python [Natural Language Toolkit](http://nltk.org), [Scikit-learn](http://scikit-learn.org), and the [Requests](http://docs.python-requests.org) library.
I used a Naive Bayes model to predict edit wars based on word frequencies, word counts, and density of references.

This was my final project for my college machine learning class.
`final_submission.pdf` is a document explaining this project in-depth.
If you're more interested in looking directly at the code, you can look in the
`src/` directory, which contains the following files:
 * `scraper.py`: This downloads articles from Wikipedia and extracts the contents out of the HTML.
 * `analyze_text.py`: This parses the raw content of a wikipedia page. It filters out stopwords, lemmatizes the remaining words, and then converts the result into a "bag-of-words".
 * `calculate_controversy.py`: This calculates articles' controversy scores using the method described in [this paper](https://arxiv.org/ftp/arxiv/papers/1305/1305.5566.pdf).
 * `naive_bayes.py`: This runs the actual machine learning algorithm which predicts how likely it is that an article will have an edit war.
 * `final.py`: This file contains miscellaneous utility functions used throughout the other Python files.

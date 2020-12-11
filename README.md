# Project Overview

The goal of the project was to explore Airbnb listings in London, from a host’s perspective, and predict guest review scores based on a certain property's attributes.
The goal of the project was to explore Airbnb listings in London, from a host’s perspective, and predict guest review scores based on their property's attributes.

Ultimately this may just have the potential to become the one-stop shop tool for an Airbnb host when managing and optimising their listing offering (...maybe!).

Data source: [Inside Airbnb](http://insideairbnb.com/)<br>

Status - completed (version 1)

## Team
Miles Tomlinson - [GH profile](https://github.com/milestommo)<br>
Ed Landamore - [GH profile](https://github.com/OrthoLoess)<br>
Elsa Lebrun-Grandie - [GH profile](https://github.com/ElsaLGF)<br>
Leone Cavicchia - [GH profile](https://github.com/leoncav)

## Methods
- Data exploration<br>
- Inferential statistics<br>
- Data visualisation<br>
- Machine learning/predictive modelling<br>
- Natural Language Processing<br>
- App user interface design

## Tech
- SQL<br>
- Python (Jupyter)<br>
- Pandas<br>
- Numpy<br>
- Matplotlib<br>
- Seaborn<br>
- Scikit-Learn<br>
- NLTK<br>
- Miro Scratchpad<br>
- Streamlit / HTML

# Project Description
- Inspired by the wealth of data provided by Inside Airbnb, we chose to explore a listing’s review score and its relationship to the features that a property offers its guests
- The early stage of the project prioritised on what the end product would look like and how it could offer real value to hosts who wanted more insight on which features to address or install in order to improve a guest’s experience
- Miro was used to design the app wireframes and visualise the user flow
- The next stage centred around data understanding and exploration. With so much data collated for each listing (c 90 dataframe columns), the trick was to shortlist the most potentially influential features for the predictive model by undergoing multiple phases of feature prioritisation
- Pandas and Matplotlib were used to understand/visualise the make up of each feature while a dummy model regressor was used to highlight the more influential features in relation to the review score
- In the modelling phase, we put K Means clustering to good use along with manual grouping in Pandas to identify groups of listings that share a common set of fixed attributes that a host wouldn’t necessarily be able to change (eg borough location, number of bedrooms, property type, etc). This allowed the app to offer the functionality of being able to compare vs other hosts with similar properties
- The offering to the host was enhanced by applying NLP methods to the verbatim review feedback left by guests, with a focus on the top rated listings in each group allowing the host to leverage the qualitative insights available to them
- The final linear regression model used a set of features chosen to minimise multicollinearity. It used l2 regularisation to help control overfitting on the training set.
- Finally, all of this led to the creation of an interactive front end that would provide information about a host’s listing, the group a host belonged to and how the most influential features could be dialled up or down to positively, or negatively, affect the review score.

# What's next?
Initially we constrained ourselves to creating an MVP, get it live and receive user feedback. However, during version one, there were many other avenues parked for the roadmap.
- Expand to other cities, exploring any different relationships between attributes and review scores
- Offer the service to new hosts, who haven't yet defined their offering or price/night, to help gauge where to pitch their property
- Refine the selection and combination of features that feed the model, to strengthen the prediction

# Startup the project

The initial setup.

Create virtualenv and install the project:
```bash
  $ sudo apt-get install virtualenv python-pip python-dev
  $ deactivate; virtualenv ~/venv ; source ~/venv/bin/activate ;\
    pip install pip -U; pip install -r requirements.txt
```

Run the streamlit server with
```bash
  $ streamlit run fivestar/five-star.py
```

# Data Storage

* `<Data-Dir>`
  * `profiles.json`
  * `<Profile-Name>_feedback.json`
  * `subscriptions.json`
  * `content.json`


# Endpoints

### GET `/`
Main Web UI and Viewer Page. Only serves the HTML

### GET `/content/<profile>`
Gets recommended content for a given profile

### GET `/profiles`
Get names of all available Profiles

### POST `/profiles`
Create a new Profile

### POST `/feedback`
Endpoint to provide feedback on recommended content


# `~/presearcher.json` File Structure

Contents (with default values shown):

```json
{
    // Main data storage location
    "data_dir": "/var/lib/presearcher/",

    // Data re-fetching interval (in seconds)
    "refresh_interval": 500,

    // Re-Training interval (in seconds)
    "retrain_interval": 86400,

    // Time Window Size (in days)
    "time_window": 14
}
```


# `profiles.json` file structure

Very simple json file that stores the list of currently active profiles

Contents:

```json
[
    "alex",
    "john",
    // ...
    "sam"
]
```


# `<Profile-Name>_feedback.json` file structure

Storage for feedback received on articles presented. Used for re-training models for specific profiles

Contents:

```json
[
    {
        "label": "pos",
        "content": {
            "title": "A Bi-layered Parallel Training Architecture for Large-scale Convolutional Neural Networks.",
            "description": "Benefitting from large-scale training datasets and the complex training network, ... improves the training performance of CNNs while maintaining the accuracy.",
            "timestamp": "2018-10-17T10:07:31",
            "link": "http://arxiv.org/abs/1810.07742",
            "authors": [
                "Jianguo Chen",
                "Kashif Bilal",
                // ...
                "Philip S. Yu"
            ]
        }
    },

    // ...

    {
        "label": "neg",
        "content": {
            "title": "Methods of identifying animals from instagram photos"
            // ...
        }
    }
]
```


# `subscriptions.json` file structure

Storage for all subscriptions to original RSS feeds

Contents:

```json
[
    "http://arxiv.org/rss/math-ph",
    "http://arxiv.org/rss/stat",
    "http://arxiv.org/rss/cs"
]
```


# `content.json` file structure

Storage for all content fetched from the subscriptions that was published within the time window.

```json
{
    "http://arxiv.org/abs/1810.07742": {
        "title": "A Bi-layered Parallel Training Architecture for Large-scale Convolutional Neural Networks.",
        "description": "Benefitting from large-scale training datasets and the complex training network, ... improves the training performance of CNNs while maintaining the accuracy.",
        "timestamp": "2018-10-17T10:07:31",
        "link": "http://arxiv.org/abs/1810.07742",
        "authors": [
            "Jianguo Chen",
            "Kashif Bilal",
            // ...
            "Philip S. Yu"
        ],
        "profiles": {
            "alex": 0.71,
            "john": 0.29,
            // ...
            "sam": 0.97
        }
    }
}
```

<div align="center">

# Happy Holding
**Ring Ring! Happy Holding :)**

---

</div>

## :beginner: About
**Waiting on the phone** can be a painful and tedious experience. Nothing is more annoying than hearing  _** the same elevator song**_ restart over and over... Why does a **mundane activity** that we all have to go through have to be so unproductive? 
 
We all agreed that this time would be better spent in a more **enjoyable** and **productive** way. With so many individuals now unemployed and tight on money, choosing the right financial service is crucial. This is where we thought, **what better opportunity to improve the financial literacy of individuals in need than while on hold?**
 
By improving the financial literacy of customers while on hold, we realized we could help them become aware of critical services that they can discuss with representatives. This helps customers capitalize on their time spent with representatives. As well, we enable financial institutions to deliver more services and collect helpful information about their customers to shape their marketing and **improve future experiences**. 

<p float="left">
 <img src="https://challengepost-s3-challengepost.netdna-ssl.com/photos/production/software_photos/001/293/373/datas/gallery.jpg" width="400" /><br/>
 <img src="https://challengepost-s3-challengepost.netdna-ssl.com/photos/production/software_photos/001/293/369/datas/gallery.jpg" width="400" />
</p>


## :electric_plug: Development Setup

This project is built using [Flask](http://flask.pocoo.org/) and [Twilio](https://www.twilio.com/)'s APIs.

To try it out for yourself:

1. Clone this repository and `cd` into it.

   ```bash
   $ git clone git@github.com:gracewgao/happy-holding.git
   $ cd happy-holding
   ```


1. Create a new virtual environment.

   ```bash
   $ pip install virtualenv
   $ virtualenv venv
   ```
   
    - On Mac:

        ```bash
        source venv/bin/activate
        ```
   
   - On Windows:
    
        ```bash
        venv\Scripts\activate
        ```
   

1. Install the dependencies.

    ```bash
    pip install -r requirements.txt
    ```


1. Start the server.

    ```bash
    python manage.py runserver
    ```


1. Make your application accessible to the wider Internet using [ngrok](https://ngrok.com/).

    ```bash
    ngrok http 5000 -host-header="localhost:5000"
    ```


1. Configure Twilio to call your webhooks

  - Configure Twilio to call your application when calls are received in your [*Twilio Number*](https://www.twilio.com/user/account/messaging/phone-numbers).
  - The voice url should look something like this:

    ```
    http://<your-ngrok-subdomain>.ngrok.io/happy/welcome
    ```

# Policy Lab Test Website
Wagtail site for testing model translation on policylab

## Install:
<pre><code>git clone <\insert_clone_url\>
cd policylab
python3 -m venv plab/env
source plab/env/bin/activate
pip install wagtail
pip install -r requirements.txt
pip install wagtail-modeltranslation

[this is a test]




</code></pre>

## How to run:
<pre><code>cd policylab
source plab/env/bin/activate
python manage.py runserver
</code></pre>

Then, navigate to http://127.0.0.1:8000/admin to see CMS!

## Login info
username: admin
password: policylab

## Push changes
python manage.py makemigrations
python manage.py migrate

## Database
Found at <code>policylab/db.sqlite3</code> <br>
The table <code>home_transhomepage</code> stores text for /home page.


## Troubleshooting
Try replacing python with python3!

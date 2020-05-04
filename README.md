# Automatic Translation Workflow for Wagtail Site 
This is a demo site that demonstratse how a 3rd party Translation API can be integrated into a Wagtail Site. 
<ul>
<li><code>trans_home_page</code> in <code>models.py</code> is a fully translatable page, where changes made to the English text are detected and sent to a 3rd party translation API (Gengo). When translations are returned, it is updated in the database and displayed in the user's language. </li>
<li><code>lang_bar.html</code> demonstrates how you can make a language dropdown on your site to allow your users to choose which language they would like to use.</li>
<li>Languages you wish to support can be added to <code>settings/languages.csv</code></li>
</ul>

## Install:
<pre><code>git clone <\insert_clone_url\>
cd translation-flow
python3 -m venv plab/env
source plab/env/bin/activate
pip install wagtail     
pip install -r requirements.txt
pip install wagtail-modeltranslation
</code></pre>

## How to run:
<pre><code>cd translation-flow
source plab/env/bin/activate
python manage.py runserver</code></pre>

Then, navigate to http://127.0.0.1:8000/admin to see CMS!

## Login info
username: admin
password: policylab

## Push database changes
<pre><code>python manage.py makemigrations
  python manage.py migrate</code></pre>

## Database
Found at <code>translation-flow/db.sqlite3</code> <br>
The table <code>home_transhomepage</code> stores text for /home page.

## Troubleshooting
Try replacing python with python3!

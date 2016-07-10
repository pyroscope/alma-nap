ALMA-NAP Web Engine
===================

*Ansible-powered setup of a Linux web host with MySQL and ACME-enabled Nginx running applications written in Python and/or PHP.*

.. contents:: **Contents**


What is It?
-----------

*ALMA-NAP* uses *Ansible* to set up a working *Linux*-based webserver environment
comprised of *MySQL*, an *ACME*-enabled *Nginx* (i.e. having “Let's Encrypt” certificates),
and applications written in *Python* and/or *PHP*. “Alma nap” also means “apple day”
in Hungarian, whatever you make of that —
maybe ‘an apple (a) day keeps the self-signed certificate away’. :grinning:

By default, a HTTPS-only setup is created, with HTTP supported only for
the necessary ACME callbacks used during certificate signing.
`ufw` is installed and used to manage port 80 dynamically during the
certificate signing and renewal process, unless port 80 was open to start with.

*ALMA-NAP* is MIT-licensed.

If you have questions or need help, please use the `pyroscope-users`_ mailing list
or the inofficial ``##rtorrent`` channel on ``irc.freenode.net``.

**WARNING:** This project is not feature-complete yet, consider it beta.
The parts that are committed are tested and do work,
but expect changes regarding the structure of the configuration values and such.


How Do I Use It?
----------------

The Big Picture
^^^^^^^^^^^^^^^

*Ansible* works by remotely controlling a *target host* to provision
software and its configuration automatically.
If you're new to *Ansible*, it's highly recommended to watch their `Quickstart Video`_
and read the `Getting Started`_ guide *now*.

At the moment, this project only supports Debian-like Linux distributions as the target.
Specifically, the stable 64bit server releases of *Debian* (Jessie) or *Ubuntu* (Xenial)
are recommended; their previous versions should also work (*Wheezy* and *Trusty*).
You also need a Linux, BSD, Mac OSX, or other POSIX system as the controlling computer.
On Windows, start a VM with the latest Ubuntu LTS (Xenial).

Before you begin, consider reading this whole README to the end, so that you know what's
ahead of you, and also know about customization options you might want to apply.


Preparing Your Workstation
^^^^^^^^^^^^^^^^^^^^^^^^^^

First, check out this repository and call the working environment bootstrapper:

.. code-block:: shell

    git clone https://github.com/pyroscope/alma-nap.git
    cd alma-nap
    ./bootstrap.sh
    . .env

It creates a Python virtualenv and installs some Python tools into it.
This includes *Ansible v1.9.6*, so you don't have to worry about
having the correct version installed on your workstation.

Next, define a moniker for the *target host* in the ``~/.ssh/config`` file
— create one if it doesn't exist yet.
You need to change ``Host`` and ``HostName`` to fitting values.

.. code-block:: ini

    Host alma-nap-dev
        HostName www.example.com
        User deploy
        IdentityFile ~/.ssh/deploy
        IdentitiesOnly yes

It is recommended you use the ``deploy`` user and its key as shown,
as the rest of the documentation works with that user account.
We'll create a SSH key for it later on.
Also, everytime you see the value ``example-host`` below,
replace it with your ``Host`` value.

Also create a custom *Ansible* inventory file similar to the ``hosts`` example
— call it ``myhosts`` and add the following:

.. code-block:: ini

    # Ansible Host Inventory

    [www]
    example-host

    [gitlab]
    # example-host

If you want `Gitlab CE`_ installed, uncomment the second entry.


Preparing Your Target Host
^^^^^^^^^^^^^^^^^^^^^^^^^^

In a dedicated terminal window, open a ``root`` shell to your target host.
Keep this open **ALL THE TIME** since the ``security`` role hardens your SSH server,
and depending on your exact setup and login procedure you could lock yourself out.
That SSH window is your life-line to fix things, especially if you have no
physical access to the target host.

Commands that should be entered into that terminal are marked with ``root@example-host#`` further below,
while ``you@workstation$`` indicates commands that should be run in the project working directory.

**IMPORTANT:** While most configuration goes to dedicated user accounts,
some global files are affected that you might have customized beforehand.
So if the target host is not a brand-new machine with a pristine OS install,
**make a backup of of your /etc and webserver directories** before you continue, for example using
``( cd / && tar cvfz /root/etc+www-bak-$(date +'%Y-%m-%d-%H%M').tgz etc var/www )``.

Execute your first ``ansible-playbook`` run with a combination of
``--user=REMOTE_USER``, ``--ask-pass``,
``--become``, ``--become-user=BECOME_USER``, ``--ask-become-pass``,
and ``--become-method=BECOME_METHOD``.
Not all of these are needed, use a sensible combination,
e.g. ``--user=root --ask-pass`` for an initial ``root`` login with a password,
which is a common way that credentials for a new cloud server are handed to you.

The ``accounts`` role will then add the configured admin accounts, by default a user
named ``deploy``. Note that you need to provide the public key of that user,
to create a new one use this command:

.. code-block:: shell

    you@workstation$
    ssh-keygen -b 4096 -t rsa -C "Ansible Deployment" -f ~/.ssh/deploy

Some minimal configuration regarding the target host is also needed, so
add a file named ``host_vars/«example-host»/main.yml`` to the project directory.

.. code-block:: yaml

    ---
    ansible_sudo: true

    motd_description: "SHORT SERVER DESCRIPTION HERE"
    nginx_server_name: "{{ ansible_fqdn }}"

An example file is in ``host_vars/alma-nap-dev/main.yml``.

The next call does the initial setup, installing some basic packages

.. code-block:: shell

    you@workstation$
    ansible-playbook -i myhosts site.yml -l alma-nap-dev -t base,acc --user=root --ask-pass

… set a sudo password for your new account…

.. code-block:: shell

    root@example-host#
    passwd deploy

Now insert this password into a new file named ``host_vars/«example-host»/secrets.yml``
with the following content:

.. code-block:: yaml

    ---
    ansible_sudo_pass: YOUR_DEPLOY_ACCOUNT_PASSWORD_HERE


… test the final connection…

.. code-block:: shell

    you@workstation$ ansible dev -i myhosts -m setup -a "filter=*distribution*"
    alma-nap-dev | success >> {
        "ansible_facts": {
            "ansible_distribution": "Debian",
            "ansible_distribution_major_version": "8",
            "ansible_distribution_release": "jessie",
            "ansible_distribution_version": "8.5"
        },
        "changed": false
    }


“Let's Encrypt” Registration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Initial Full Run
^^^^^^^^^^^^^^^^



Completing Your Setup
^^^^^^^^^^^^^^^^^^^^^

Disable Root and Password Login
-------------------------------

So that people *not* reading this documentation don't lock themselves
out of their servers, the two critical values regarding this
have *unsecure* but *safe* defaults.
To rememedy that, add the following to the ``group_vars/all/main.yml`` file:

.. code-block:: yaml

    ---
    sshd_PasswordAuthentication: false
    sshd_PermitRootLogin: false

Then re-run the playbook as follows:

.. code-block:: shell

    you@workstation$
    ansible-playbook -i myhosts site.yml -l example-host -t sec

Now test in a new terminal that you can still access the server by
logging in to the `deploy`` account, which should always work,
since that is a non-root account with pubkey authentication.
But better make sure…


PHP Application Considerations
------------------------------

The default configuration comes with multiple PHP hardening settings
that might break some features of your application.
Please check the following points and if there is a conflict,
either change you code or adapt the default values.

* Make sure you're not relying on side effects of assertions.




More Technical Details
----------------------


.. _`pyroscope-users`: http://groups.google.com/group/pyroscope-users
.. _`Quickstart Video`: https://docs.ansible.com/ansible/quickstart.html
.. _`Getting Started`: https://docs.ansible.com/ansible/intro_getting_started.html
.. _`Gitlab CE`: https://about.gitlab.com/features/#community

# products

Repo for the products team for NYU DevOps

## Prerequisite Installation using Vagrant VM

Initiating a development environment requires  **Vagrant** and **VirtualBox**. if you don't have this software the first step is down download and install it.

Download [VirtualBox](https://www.virtualbox.org/)

Download [Vagrant](https://www.vagrantup.com/)

Then all you have to do is clone this repo and invoke vagrant:

```bash
    git clone https://github.com/nyu-devops/lab-flask-rest.git
    cd lab-flask-rest
    vagrant up
    vagrant ssh
    cd /vagrant
```


## Vagrant shutdown

When you are done, you should exit the virtual machine and shut down the vm with:

```bash
 $ exit
 $ vagrant halt
```

If the VM is no longer needed you can remove it with:

```bash
  $ vagrant destroy
```





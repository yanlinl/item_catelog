### How to Run?

#### PreRequisites
  * [Python ~2.7](https://www.python.org/)
  * [Vagrant](https://www.vagrantup.com/)
  * [VirtualBox](https://www.virtualbox.org/)


#### Setup Project:
  1. Install <a href="https://www.vagrantup.com/">Vagrant</a> and <a href="https://www.virtualbox.org/wiki/Downloads">VirtualBox.</a>
  2. Clone the repository to your local machine:
     <pre>git clone https://github.com/yanlinl/item_catelog.git</pre>

#### Launch Project
  1. Launch the Vagrant VM using command:
  
  ```
    $ vagrant up
  ```
  2. Change to the directory where the program is cloned.
  3. Run your application within the VM
  
  ```
    $ python run_project.py
  ```
  4. Access and test your application by visiting [http://localhost:8000](http://localhost:8000).
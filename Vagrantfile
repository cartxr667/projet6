Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"

  config.vm.define "pg1" do |m|
    m.vm.hostname = "pg1"
    m.vm.network "private_network", ip: "192.168.56.11"
    m.vm.provider "virtualbox" do |vb|
      vb.name = "pg1"
      vb.memory = 1024
      vb.cpus = 1
    end
  end

  config.vm.define "pg2" do |m|
    m.vm.hostname = "pg2"
    m.vm.network "private_network", ip: "192.168.56.12"
    m.vm.provider "virtualbox" do |vb|
      vb.name = "pg2"
      vb.memory = 1024
      vb.cpus = 1
    end
  end
  config.vm.define "lb1" do |lb1|
    lb1.vm.hostname = "lb1"
    lb1.vm.network "private_network", ip: "192.168.56.10"
    lb1.vm.provider "virtualbox" do |vb|
      vb.memory = 1024
      vb.cpus = 1
    end
  end
  config.vm.define "lb2" do |lb2|
    lb2.vm.hostname = "lb2"
    lb2.vm.network "private_network", ip: "192.168.56.13" # IP réelle de lb2
    lb2.vm.provider "virtualbox" do |vb|
      vb.name = "lb2"
      vb.memory = 1024
      vb.cpus = 1
    end
  end

  config.vm.define "app1" do |app1|
    app1.vm.hostname = "app1"
    app1.vm.network "private_network", ip: "192.168.56.20"
    app1.vm.provider "virtualbox" do |vb|
      vb.memory = 1024
      vb.cpus = 1
    end
  end

  config.vm.define "app2" do |app2|
    app2.vm.hostname = "app2"
    app2.vm.network "private_network", ip: "192.168.56.21"
    app2.vm.provider "virtualbox" do |vb|
      vb.memory = 1024
      vb.cpus = 1
    end
  end
  config.vm.define "zabbix" do |zabbix|
    zabbix.vm.hostname = "zabbix"
    zabbix.vm.network "private_network", ip: "192.168.56.30"
    zabbix.vm.provider "virtualbox" do |vb|
      vb.name = "zabbix"
      vb.memory = 2048 # Zabbix a besoin d'un peu plus de RAM
      vb.cpus = 2
    end
  end
end

include aventurella-ruby
include aventurella-github
include aventurella-git
include aventurella-apache2
include aventurella-ntp
include aventurella-vim

aventurella-ruby::gem {'sass':}

user{'ctflorals':
    ensure     => "present",
    groups     => ['www-data'],
    home       => "/home/ctflorals",
    shell      => "/bin/bash",
    managehome => true,
}

file{'/var/www/ctflorals':
    ensure => link,
    target => "/home/ctflorals/app/www",
    require => [User[ctflorals], Package['apache2'], Aventurella-Github::Clone['aventurella/ctflorals.git']],
    notify => Service[apache2]
}

aventurella-apache2::module {'enable_apache_modules':
    modules => ['rewrite'],
    enable => true,
}

aventurella-apache2::vhost {'ctflorals':
    docroot        => '/var/www/ctflorals',
    server_name    => 'ctflorals.com',
    server_aliases => ['www.ctflorals.com'],
    allow_override => true,
}

aventurella-github::clone{'aventurella/ctflorals.git':
    path  => '/home/ctflorals/app',
    owner => 'ctflorals',
    group => 'www-data',
    require => [User[ctflorals]]
}

exec { 'compile-css':
        command => "scss --force --update /home/ctflorals/app/www/resources/css/src:/home/ctflorals/app/www/resources/css",
        require => [ Aventurella-ruby::Gem['sass'], Exec['aventurella/ctflorals.git'] ],
        path => ["/usr/bin", '/usr/local/bin']
}

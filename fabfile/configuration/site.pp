
include aventurella-github
include aventurella-git
include aventurella-apache2
include aventurella-ntp
include aventurella-vim

aventurella-apache2::module {'enable_apache_modules':
    modules => ['rewrite'],
    enable => true,
}

aventurella-github::clone{'aventurella/ctflorals.git':
    path  => '/var/www/ctflorals',
    owner => 'www-data',
    group => 'www-data'
}

aventurella-apache2::vhost {'ctflorals':
    docroot        => '/var/www/ctflorals/www',
    server_name    => 'ctflorals.com',
    server_aliases => ['www.ctflorals.com'],
    allow_override => true,
}


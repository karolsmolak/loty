let host_url = 'http://localhost:8000';

var app = angular.module('crews', ['ngCookies', 'ngAnimate']);

app.config(function ($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
});


app.controller('user_controller', function ($scope, $rootScope, $http, $cookies) {
    $("#loginbtn").popover({
        content: "Upewnij się, że wprowadzone dane są poprawne.",
        placement: "bottom",
        trigger: "manual"
    });

    $("#search").popover({
        content: "Brak lotu o podanym numerze.",
        placement: "bottom",
        trigger: "manual"
    });

    $scope.username = $cookies.get("username");
    $rootScope.logged = false;

    if ($scope.username) {
        $rootScope.logged = true;
        $http.defaults.headers.common.Authorization = 'JWT ' + $cookies.get("token");
    }

    $scope.login = function() {
        $http.post(host_url + '/api/obtain-token', $scope.login_form).then(
            function success(response) {
                $cookies.put('token', response.data['token']);
                $cookies.put('username', $scope.login_form.username);
                $http.defaults.headers.common.Authorization = 'JWT ' + $cookies.get("token");
                $rootScope.logged = true;
                $scope.username = $scope.login_form.username;
            }, function failure(response) {
                $("#loginbtn").popover('show');
                setTimeout(function () {
                    $("#loginbtn").popover('hide');
                }, 1900);
            });
    };

    $scope.logout = function() {
        $rootScope.logged = false;
        $cookies.remove('token');
        $cookies.remove('username');
    };
});

app.controller('flight_controller', function ($scope, $http, $cookies) {
    let get_flight_url = function (flight_id) {
        return host_url + '/api/flights/' + flight_id;
    }

    $scope.load_workers = function() {
        $http.get(host_url + '/api/workers').then(function (response) {
            $scope.workers = response.data;
        })

    }

    $scope.load_workers();

    $scope.load_flight = function(flight_id) {
        $http.get(get_flight_url(flight_id))
             .then(function success(response) {
                 $scope.flight = response.data;
             }, function failure(response) {
                $("#search").popover('show');
                setTimeout(function () {
                    $("#search").popover('hide');
                }, 1900);
             });
    };

    $scope.remove_worker = function (worker_id) {
         $http.delete(get_flight_url($scope.flight.id) + '/crew/' + worker_id)
         .then(function success(response) {
             $scope.load_flight($scope.flight.id);
         }, function failure(response) {
            console.log("failure");
         });
    };

    $scope.add_worker = function () {
        $http.post(get_flight_url($scope.flight.id) + '/crew/' + $scope.new_worker.id)
        .then(function success(response) {
            $scope.load_flight($scope.flight.id);
        }, function failure(response) {
            console.log("failure");
        });
    };

    $scope.make_captain = function (worker_id) {
     $http.put(get_flight_url($scope.flight.id) + '/crew/' + worker_id)
     .then(function success(response) {
         $scope.load_flight($scope.flight.id);
     }, function failure(response) {

     });
    };
});
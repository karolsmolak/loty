let host_url = "http://" + window.location.host;

var app = angular.module('crews', ['ngAnimate', 'ngStorage']);

app.config(function ($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
});

let show_popover = function (id) {
    let element = $("#" + id);
    element.popover('show');
    setTimeout(function () {
        element.popover('hide');
    }, 1900);
}

app.controller('user_controller', function ($scope, $rootScope, $http, $localStorage) {
    $("#loginbtn").popover({
        content: "Upewnij się, że wprowadzone dane są poprawne.",
        placement: "bottom",
        trigger: "manual"
    });

    $rootScope.logged = false;
    $scope.username = $localStorage.username;

    if ($scope.username) {
        $rootScope.logged = true;
        $http.defaults.headers.common.Authorization = 'JWT ' + $localStorage.token;
    }

    $scope.login = function() {
        $http.post(host_url + '/api/obtain-token/', $scope.login_form).then(
            function success(response) {
                $localStorage.token = response.data['token'];
                $localStorage.username = $scope.login_form.username;
                $http.defaults.headers.common.Authorization = 'JWT ' + $localStorage.token;
                $rootScope.logged = true;
                $scope.username = $scope.login_form.username;
            }, function failure(response) {
                show_popover("loginbtn");
            });
    };

    $scope.logout = function() {
        $rootScope.logged = false;
        delete $localStorage.token;
        delete $localStorage.username;
    };
});

app.controller('flight_controller', function ($scope, $http) {
    let get_flight_url = function (flight_id) {
        return host_url + '/api/flights/' + flight_id;
    };

    $("#search").popover({
        content: "Brak lotu o podanym numerze.",
        placement: "bottom",
        trigger: "manual"
    });

    $scope.load_workers = function() {
        $http.get(host_url + '/api/workers/').then(function (response) {
            $scope.workers = response.data;
        });
    };

    $scope.load_workers();

    $scope.load_flight = function(flight_id) {
        if (flight_id) {
            $http.get(get_flight_url(flight_id) + '/')
            .then(function success(response) {
                $scope.flight = response.data;
                delete $scope.errors;
            }, function failure(response) {
                show_popover("search");
            });
        } else {
            show_popover("search");
        }
    };

    $scope.remove_worker = function (worker_id) {
         $http.delete(get_flight_url($scope.flight.id) + '/crew/' + worker_id + '/')
         .then(function success(response) {
             $scope.load_flight($scope.flight.id);
             delete $scope.errors;
         });
    };

    $scope.add_worker = function () {
        $http.post(get_flight_url($scope.flight.id) + '/crew/' + $scope.new_worker.id + '/')
        .then(function success(response) {
            $scope.load_flight($scope.flight.id);
            delete $scope.errors;
        }, function failure(response) {
            $scope.errors = response.data['error'];
        });
    };

    $scope.make_captain = function (worker_id) {
        $http.put(get_flight_url($scope.flight.id) + '/crew/' + worker_id + '/')
        .then(function success(response) {
            $scope.load_flight($scope.flight.id);
            delete $scope.errors;
        }, function failure(response) {

        });
    };
});
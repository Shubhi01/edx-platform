;(function (define, undefined) {
    'use strict';

    define(['jquery', 'teams/js/views/teams_tab'],
        function ($, TeamsTabView) {

            // TODO: remove-- only here for testing purposes.
            $("body").append("<div class='added'>test text</div>");

            return function () {
                var view = new TeamsTabView({
                    el: $('.team-tab-content')
                });
                view.render();
            };
        });
}).call(this, define || RequireJS.define);

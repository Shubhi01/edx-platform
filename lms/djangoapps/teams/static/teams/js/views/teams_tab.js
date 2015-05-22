;(function (define, undefined) {
    'use strict';
    // TODO: we aren't actually requirejs text!
    define(['backbone', 'underscore', 'text!teams/js/templates/teams_tab.underscore'],
        function (Backbone, _, teamsTabTemplate) {
            var TeamTabView = Backbone.View.extend({
                render: function() {
                    this.$el.html(_.template(teamsTabTemplate, {

                    }));
                    return this;
                }
            });

            return TeamTabView;
        });
}).call(this, define || RequireJS.define);

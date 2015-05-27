;(function (define, undefined) {
    'use strict';

    define(['backbone', 'underscore'],
        function (Backbone, _) {
            var TeamTabView = Backbone.View.extend({
                render: function() {
                    var template_text = $('#teams-tab-tpl').text();
                    this.$el.html(_.template(template_text));
                    return this;
                }
            });

            return TeamTabView;
        });
}).call(this, define || RequireJS.define);

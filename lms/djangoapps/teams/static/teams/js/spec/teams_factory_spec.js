define(["jquery", "js/common_helpers/template_helpers", "teams/js/teams_tab_factory"],
    function($, TemplateHelpers, TeamsTabFactory) {
        'use strict';
       
        describe("teams django app", function() {
            var teamsTab;

            beforeEach(function() {
                setFixtures("<div class='team-tab-content'></div>");
                TemplateHelpers.installTemplate('teams/templates/teams-tab');
                teamsTab = new TeamsTabFactory();
            });

            it("can require JS file in teams", function() {
                expect($("div.added").text()).toBe("test text");
            });

            it("can load templates", function() {
                expect($("body").text()).toContain("This is the new Teams tab");
            });

        });
    }
);

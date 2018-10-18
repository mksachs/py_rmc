/**
 * Created by michaelsachs on 4/9/17.
 */

function init_popup_new_encounter() {
    $("#new_encounter").prop("disabled", true);
    $.ajax({
        context: document.body,
        url: "http://127.0.0.1:5000/api/v1.0/combatants",
        type: "GET",
        success: function (result) {
            bind_popup_new_encounter(result.list);
        }
    });
}

function bind_popup_new_encounter(combatants) {
    var overlay = $("#overlay");
    $("#overlay").show();
    overlay.append(
        '<input id="encounter_name" type="text" value="Encounter Name"" />'
    );
    var combatant_string = "";
    combatants.forEach( function(combatant) {
        combatant_string += '<div class="combatant id_' + combatant.id + '">' +
            '<span class="stat name"><b>' + combatant.name + '</b></span>' +
            '<span class="stat level">' + combatant.level + '</span>' +
            '<span class="stat hit_points">hp: ' + combatant.hit_points + '</span>' +
            '<span class="stat power_points">pp: ' + combatant.power_points + '</span>' +
            '<span class="stat db">db: ' + combatant.db + '</span>' +
            '<span class="stat qb">qb: ' + combatant.qb + '</span>' +
            '<span class="stat at">at: ' + combatant.at + '</span>' +
            '<input type="checkbox" />' +
            '</div>'
    });
    overlay.append(combatant_string);
    overlay.append(
        '<input id="create_encounter" type="button" value="Create Encounter" onclick="create_new_encounter()" />'
    )
}

function create_new_encounter() {
    var encounter_name = $("#encounter_name").val();
    $.ajax({
        context: document.body,
        url: "http://127.0.0.1:5000/api/v1.0/encounters",
        type: "POST",
        data: JSON.stringify({
            name: encounter_name,
            round: 0,
            phase: 'initiative'
        }),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        failure: function(errMsg) {
            alert(errMsg);
        },
        success: function (result) {
            link_new_encounter_combatants(result.obj);
        }
    });
}

function link_new_encounter_combatants(added_encounter) {
    var overlay = $("#overlay");
    var encounter_id = added_encounter.id;

    var deferred_calls = [];
    $("#overlay .combatant").each( function(index) {
        if ($(this).children("input").is(':checked')) {
            var combatant_id = $(this).attr("class").substr(13);
            deferred_calls.push($.ajax({
                context: document.body,
                url: "http://127.0.0.1:5000/api/v1.0/combatants/" + combatant_id + "?parent=encounter&parent_id=" + encounter_id,
                type: "LINK"
            }));
        }
    });

    $.when.apply($, deferred_calls).then(
        function ( value ) {
            // Success
            $("#overlay").empty();
            $("#overlay").hide();
            $("#content").empty();
            $.ajax({
                context: document.body,
                url: "http://127.0.0.1:5000/api/v1.0/encounters?children=true",
                type: "GET",
                success: function (result) {
                    bind_encounters(result.results);
                }
            });
        },
        function ( value ) {
            // Fail
        }
    );
}

function bind_encounters(encounters) {
    $("#new_encounter").prop("disabled", false);
    var content = $("#content");
    var encounters_string = "";
    encounters.forEach( function(encounter) {
        encounters_string += '<a href="http://127.0.0.1:5000/encounters/' + encounter.id + '" class="list_link">' +
            '<div class="encounter ' + encounter.id + '">' +
            '<span class="stat name"><b>' + encounter.name + '</b></span>' +
            '<span class="stat name">' + encounter.round + '</span>' +
            '<span class="stat name">' + encounter.phase + '</span>' +
            '<span class="stat num_combatants">' + encounter.children.combatants.length + ' combatants</span>' +
            '<span class="stat date">' + encounter.updated + '</span>' +
            '</div></a>'
    });
    content.append(encounters_string);
}

function bind_encounter(encounter) {
    var dom_content = $("#content");
    var dom_controls = $("#page_controls");
    var dom_phase_advance = $("#phase_advance");
    var dom_phase_retreat = $("#phase_retreat");
    var dom_header = $("#header");
    
    document.title = "Encounter: " + encounter.obj.name + " Round: " + encounter.obj.round;

    if (dom_phase_advance.length === 0) {
        // First time
        dom_controls.append(
            '<input id="phase_advance" type="button" value="" onclick="" />'
        );
        dom_phase_advance = $("#phase_advance");
    }

    if (encounter.obj.phase === "initiative") {
        dom_phase_retreat.remove();
        dom_phase_advance.attr("value", "End Initiative");
    }
    else if (encounter.obj.phase === "actions") {
        if (dom_phase_retreat.length === 0) {
            dom_controls.prepend(
                '<input id="phase_retreat" type="button" value="Back to Initiative" onclick="" />'
            );
            dom_phase_retreat = $("#phase_retreat");
        } else {
            dom_phase_retreat.attr("value", "Back to Initiative");
        }

        dom_phase_advance.attr("value", "End Actions");
    }
    else if (encounter.obj.phase === "upkeep") {
        if (dom_phase_retreat.length === 0) {
            dom_controls.prepend(
                '<input id="phase_retreat" type="button" value="Back to Actions" onclick="" />'
            );
            dom_phase_retreat = $("#phase_retreat");
        } else {
            dom_phase_retreat.attr("value", "Back to Actions");
        }

        dom_phase_advance.attr("value", "End Round");
    }

    dom_phase_advance.attr("onclick", "advance_phase(" + encounter.obj.id + ", '" + encounter.obj.phase + "')");
    if (dom_phase_retreat.length !== 0) {
        dom_phase_retreat.attr("onclick", "retreat_phase(" + encounter.obj.id + ", '" + encounter.obj.phase + "')");
    }

    if (dom_header.length === 0) {
        dom_content.append(
            '<div id="header">' +
                '<span class="stat name"></span>' +
                '<span class="stat round"></span>' +
                '<span class="stat phase"></span>' +
            '</div>'
        );
        dom_header = $("#header");
    }

    dom_header.children(".stat.name").text(encounter.obj.name);
    dom_header.children(".stat.round").text(encounter.obj.round);
    dom_header.children(".stat.phase").text(encounter.obj.phase);

    bind_encounter_combatants(encounter.children.combatants, encounter.obj.phase)
}

function bind_encounter_combatants(combatants, current_phase) {
    var dom_content = $("#content");
    var dom_combatants = $("#combatants");

    var phase_combatant_controls;

    // if (current_phase === "initiative") {
    //     phase_combatant_controls = '<input type="text" class="roll initiative" />'
    // }
    // else if (current_phase === "actions") {
    //     phase_combatant_controls = '<div'
    // }

    if (dom_combatants.length === 0) {
        dom_content.append('<div id="combatants"></div>');
        dom_combatants = $("#combatants");
        combatants.forEach( function(combatant) {
            dom_combatants.append(
                '<div class="combatant id_' + combatant.id + '">' +
                    '<span class="stat name"></span>' +
                    '<span class="stat hit_points"></span>' +
                    '<span class="stat power_points"></span>' +
                    '<span class="stat db"></span>' +
                    '<span class="stat qb"></span>' +
                    '<span class="stat at"></span>' +
                    '<span class="controls combatant"></span>' +
                '</div>'
            );
        });

    }

    combatants.forEach( function(combatant) {
        var combatant_id = combatant.id;
        var dom_combatant = dom_combatants.children(".combatant.id_" + combatant_id);
        var dom_combatant_controls = dom_combatant.children(".controls.combatant");
        var dom_combatant_controls_initiative = dom_combatant_controls.children(".initiative");
        var dom_combatant_controls_actions = dom_combatant_controls.children(".actions");
        var dom_combatant_controls_upkeep = dom_combatant_controls.children(".upkeep");

        dom_combatant_controls_initiative.hide();
        dom_combatant_controls_actions.hide();
        dom_combatant_controls_upkeep.hide();

        dom_combatant.children(".stat.name").text(combatant.name);
        dom_combatant.children(".stat.hit_points").text(combatant.hit_points);
        dom_combatant.children(".stat.power_points").text(combatant.power_points);
        dom_combatant.children(".stat.db").text("db: " + combatant.db);
        dom_combatant.children(".stat.qb").text("qb: " + combatant.qb);
        dom_combatant.children(".stat.at").text("at: " + combatant.at);
        if (current_phase === "initiative") {
            if (dom_combatant_controls_initiative.length === 0) {
                dom_combatant_controls.append(
                    '<span class="initiative">' +
                        '<span class="control initiative">init:<input type="text" class="roll" /></span>' +
                        '<span class="control parry">parry:<input type="text" class="user_def" />%</span>' +
                    '</span>'
                );
                dom_combatant_controls_initiative = dom_combatant_controls.children(".initiative");
            }

            dom_combatant_controls_initiative.show();

        }
        else if (current_phase === "actions") {
            var parry_value = parseInt(dom_combatant_controls_initiative.children(".parry").children("input").val());
            if (isNaN(parry_value)) {
                parry_value = 0;
            } else if (parry_value > 100) {
                parry_value = 100;
            } else if (parry_value < 0) {
                parry_value = 0;
            }

            if (dom_combatant_controls_actions.length === 0) {

                dom_combatant_controls.append(
                    '<span class="actions">' +
                        '<span class="control parry"></span>' +
                    '</span>'
                );
                dom_combatant_controls_actions = dom_combatant_controls.children(".actions");
            }

            dom_combatant_controls_actions.children(".parry").text("parry: " + parry_value + "%");

            dom_combatant_controls_actions.show();

        }
        $.ajax({
            context: document.body,
            url: "http://127.0.0.1:5000/api/v1.0/combatants/" + combatant_id + "?children=true",
            type: "GET",
            success: function (result) {
                var dom_combatant = $(".combatant.id_" + result.obj.id);
                var dom_attacks = dom_combatant.children(".attacks");

                if (dom_attacks.length === 0) {
                    dom_combatant.append('<div class="attacks"></div>');
                    var dom_attacks = dom_combatant.children(".attacks");
                    result.children.attack_types.forEach( function(attack_type) {
                        dom_attacks.append(
                            '<div class="attack id_' + attack_type.id + '">' +
                                '<span class="stat name"></span>' +
                                '<span class="stat ob"></span>' +
                            '</div>'
                        );
                    });
                }

                result.children.attack_types.forEach( function(attack_type) {
                    var dom_attack = dom_attacks.children(".attack.id_" + attack_type.id);
                    dom_attack.children(".stat.name").text(attack_type.name);
                    dom_attack.children(".stat.ob").text(attack_type.ob);
                });
            }
        });
    });
}

function advance_phase(encounter_id, current_phase) {
    if (current_phase === "initiative") {
        sort_combatants();
        $.ajax({
            context: document.body,
            url: "http://127.0.0.1:5000/api/v1.0/encounters/" + encounter_id+ "?children=true",
            type: "PATCH",
            data: JSON.stringify({
                phase: 'actions'
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (result) {
                bind_encounter(result);
            }
        });
    }
}

function retreat_phase(encounter_id, current_phase) {
    if (current_phase === "actions") {
        sort_combatants();
        $.ajax({
            context: document.body,
            url: "http://127.0.0.1:5000/api/v1.0/encounters/" + encounter_id+ "?children=true",
            type: "PATCH",
            data: JSON.stringify({
                phase: 'initiative'
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (result) {
                bind_encounter(result);
            }
        });
    }
}

function sort_combatants() {
    var all_combatants = $("#combatants").children();

    all_combatants.sort(function (a, b) {
        var a_i_roll, b_i_roll, a_qb, b_qb;
        // console.debug(a);
        a_i_roll = parseInt($(a).children(".initiative").children("input").val());
        b_i_roll = parseInt($(b).children(".initiative").children("input").val());
        a_qb = parseInt($(a).children(".qb").text().substr(3));
        b_qb = parseInt($(b).children(".qb").text().substr(3));
        if (isNaN(a_i_roll)) {
            a_i_roll = 0;
        }
        if (isNaN(b_i_roll)) {
            b_i_roll = 0;
        }
        if (isNaN(a_qb)) {
            a_qb = 0;
        }
        if (isNaN(b_qb)) {
            b_qb = 0;
        }

        var a_total = a_i_roll + a_qb;
        var b_total = b_i_roll + b_qb;

        return b_total - a_total;
    });

    $("#combatants").empty();
    $("#combatants").append(all_combatants);
}
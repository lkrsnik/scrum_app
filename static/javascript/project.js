$(document).ready(function (e) {
	
	//on Load
	$(".item:first").hide();
	loadMembers();
	
	//function adds all the members that were written in before (so that you don't loose data on validation error)
	function loadMembers(){
		var text = $("#previous_members").text().split(" ");
		text.forEach(function(entry) {
			
			if (entry!="")
				addForm("form",entry);
		})
	}
	
	//function deletes a row
	function deleteForm(btn, prefix) {
        var formCount = $("p.message").size();
        if (formCount > 1) {
            // Delete the item/form
            $(btn).parents('.item').remove();
            
        }
        return false;
    }
	
	//function adds a team member
	function addForm(prefix, text) {
		// Clone a form (without event handlers) from the first form
		var row = $(".item:first").clone(false).get(0);
		
		
		//alert(text)
		$(row).find("#team_member").html(text);

		// Insert it after the last form
		$(row).removeAttr('id').hide().insertAfter(".item:last").slideDown(300);

		// Add an event handler for the delete item/form link 
		$(row).find(".delete").click(function () {
			return deleteForm(this, prefix);
		});
		
		$(row).show();
        return false;
    }
	
	//function validates if team member is already in team or if there's no member selected and throws an error
	function validateTeamMember(){
		var thisMember = $("#id_team option:selected").text();
		var errorText = "";
		if (thisMember == "---------"){
			errorText='* Select a team member.'
			
		}
		$("p.message").each(function() {
			if($(this).text()==thisMember){
				errorText='* Member is already in team.'
			}
				
		});
		$("#id_team").parent().parent().find(".errorwrapper").html(errorText);
		if (errorText=="")
			return true;
		else
			return false;
	}
	
	//FUNCTIONS FROM CLICKS
	
	//Add team member button
	$("#add").click(function () {
		if(validateTeamMember())
			return addForm("form", $("#id_team option:selected").text());
		return false;
    });
	
	//Delete team member button
	$(".delete").click(function () {
        return deleteForm(this, "form");
    });
	
	//Add project button
	$("#complete_form").click(function () {
		$("#id_team").val( "---------" );
		var postText = "";
		a=0;
		$("p.message").each(function() {
			if($(this).text()!=""){
				if(a==0)
					postText += $(this).text();
				else
					postText += " " + $(this).text();
				a=a+1;
			}	
		});
		if (postText == ""){
			$("#id_team").parent().parent().find(".errorwrapper").html("* Select at least one team member.");
			//e.preventDefault();
			return false;
		}
		$("#write_team_members").val(postText)
    });
});

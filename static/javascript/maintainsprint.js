$(document).ready(function (){
	 $('.target').click(function(e) {
		 // get form associated with the button
		 var form = $(this)

		var x;
		var r=confirm("Do you really want to delete sprint?");
		if (r==true)
		  {
		  x="You pressed OK!";
		  }
		else
		  {
		  e.preventDefault();
		  x="You pressed Cancel!";
		  }
		document.getElementById("demo").innerHTML=x;
	 });
	});
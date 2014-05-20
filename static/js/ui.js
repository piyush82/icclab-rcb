$(document).ready(function(){
	$("#queryForm").hide();

	$("#id_radio_0").click(function(){
    		$("#queryForm").show();
});
	$("#id_radio_1").click(function(){
    		$("#queryForm").hide();
});

	$('#id_resources').on("change",function() {
   		var selected = $(this).val();
		var pom_resources = document.getElementById("var_resources").value;
		var var_resources=pom_resources.split(",");
		var pom_meters = document.getElementById("var_meters").value;
		var var_meters=parseJSON(pom_meters);
		count=0;
		brojac=0;
		for (var i in var_resources){
    			var r=var_resources[i]
			var n1=r.indexOf("'")
			var n2 = r.indexOf("'", n1 + 1);
			var res = r.substring(n1+1,n2);
			if (res==selected){
				var ok="ok"
				for ( var j in var_meters) {
					
					if (i==j){
						for ( var k = 0, m = var_meters[j].length; k < m; k++ ) {
							$("#results").html(var_meters[j][k]);
					brojac++
			count++
		}}}}}

});
});

$(function() {
	$("#id_dateStart").datepicker({ dateFormat: 'yy-mm-dd' });
	$("#id_dateEnd").datepicker({ dateFormat: 'yy-mm-dd' });

});






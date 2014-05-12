$(document).ready(function(){
	$("#queryForm").hide();
	$("#id_radio_0").click(function(){
    		$("#queryForm").show();
});
	$("#id_radio_1").click(function(){
    		$("#queryForm").hide();
});
});

$(function() {
	$("#id_dateStart").datepicker({ dateFormat: 'yy-mm-dd' });
	$("#id_dateEnd").datepicker({ dateFormat: 'yy-mm-dd' });

});






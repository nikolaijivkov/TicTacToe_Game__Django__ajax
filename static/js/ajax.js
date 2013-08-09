$( document ).ready(function(){
	//getBoardAlert();
    setInterval(getBoard , 2500); //while with interval 5sec :) nice little thing
});

function getBoardAlert(){
	alert("trying to get the board");
}

function getBoard(){
	//getBoardAlert();
	$.ajax({
		type: "GET",
		url: "/game/get_board/",
		success: getBoardSuccess,
        error: getBoardError,
		dataType: "html"
	});
}

function getBoardSuccess(data, textStatus, jqXHR){
	//alert('request success');
    $('#game_table').html(data);
}
function getBoardError(xhr, textStatus, errorThrown){
    alert('request error');
}

function reload_page(){
    window.location.reload(true);
}
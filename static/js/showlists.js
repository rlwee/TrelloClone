$(document).ready(function(){
    
    boardButton();
    createBoard();
    
    listCreate();
    
   
    
    const $listContainer = $('.list-container');
    const url = $listContainer.data('url');


    
    

    $.ajax({
        url: url,
        method: 'GET'
    }).done(function(response){
        $listContainer.html(response);
        var listsElement = $('.list-section');
        

        var $cardContainer = $('.card-container');
        
        $($cardContainer).each(function(index){
            var cardURL = $(this).data('url');
            
            loadCards(cardURL, $(this));
            
            //console.log(cardURL, 'url');
        });


        var $listContent = $('.list-content');

        $('.list-content').on('blur', function(){
            var url = $(this).data('update');
            var oldValue = $(this).data('title');
            var newTitle = $(this).text();
            var csrf = $('input[name="csrfmiddlewaretoken"]').val();
            console.log(csrf, 'test')
            
           
            if(newTitle.length == 0) {
                $(this).text(oldValue);
            } else {
                $.ajax({
                    
                    url: url,
                    method: 'POST',
                    data: {'title': newTitle, 'csrfmiddlewaretoken':csrf}
                }).done(function(response){
                    console.log(response)
                    
                });
            }
        });




    })
    

    



    function loadCards(url, element){
        $.ajax({
            url: url,
            method: 'GET',
        }).done(function(response){
            element.html(response);
            //var cardsElement = $('.card-section');
 

            dragCard();
            editCard();
            addButton();
            
        
    })

}


    function editCard(){
        $('.card-content').on('blur', function(){
            var url =  $(this).data('update');
            var oldValue = $(this).data('title');
            var newTitle = $(this).text();
            var csrf = $('input[name="csrfmiddlewaretoken"]').val();

            if (newTitle.length == 0){
                $(this).text(oldValue);
            } else {
                $.ajax({
                url: url,
                method: 'POST',
                data: {'title': newTitle, 'csrfmiddlewaretoken':csrf}
            }).done(function(response){
                console.log(response)
                
            })
            }
            
        });
    }


    function addButton(){
        $('#card-modal').on('shown.bs.modal',function(event){
            var remoteUrl = $(event.relatedTarget).data('remote');
            var modal = $(this);

            $.ajax({
                 'method': 'get',
                 'url': remoteUrl
            }).done(function(response){
                    modal.find('.modal-body').html(response);
                    //console.log(response, 'bla')
                }); 

        });
    }

        $(document).on('submit','.card-form',function(event){
            event.preventDefault();
            var cardFormAction = $(this).attr('action');
            console.log(cardFormAction, 'action');
            var cardData = $(this).serialize();
        
            $.ajax({
                url: cardFormAction,
                data: cardData,
                method: 'POST',
            }).done(function(response){
                event.preventDefault();
                var listID = response.list_id;
                var cardContainer = $(`#list-${listID}`);
                var card_template = `<li class="card-content" data-title="" data-update="/board/${response.board_id}/list/${response.list_id}/card/${response.id}/update/" contenteditable="true">${response.title}</li>`;
                var cards_template = `<div class="draggable shadow-sm p-3 mb-5 bg-white rounded ui-draggable ui-draggable-handle" id="draggable" data-url="/board/${response.board_id}/list/${response.list_id}/card/${response.id}/dragged/card/" data-id="${response.id}"> 
  
                <button type="button" id="carddetail-${response.id}" data-id="${response.id}" data-title="${response.title}" class="btn btn-primary-card" data-remote="/board/${response.board_id}/list/${response.list_id}/card/${response.id}/" data-toggle="modal" data-target="#card-view-modal">${response.title}
                  </button>

                  <img class="imgdrag" src="/static/images/dragcardicon.png" width="20" ,="" height="20">

                </div>`
                $(cardContainer).find('.list-view').append(cards_template);
                $('#card-modal').modal('hide');
                
                console.log(response, 'done');
            }).fail(function(response){
                //alert('invalid input');
                var errorMessage = '<p>This field is required</p>';

                $('.error-card').html(errorMessage);


            });
        });
    



    function boardButton(){
        $('#board-modal').on('shown.bs.modal',function(event){
            var remoteUrl = $(event.relatedTarget).data('remote');
            var modal = $(this);

            $.ajax({
                'method':'get',
                'url': remoteUrl
            }).done(function(response){
                modal.find('.modal-body').html(response);
                editBoard();

                
            })
            
        });
    }

    function editBoard(){
        $(document).on('submit', '.board-form', function(event){
            event.preventDefault();
            var boardFormAction = $(this).attr('action');
            var boardData = $(this).serialize();
            $.ajax({
                url:boardFormAction,
                data: boardData,
                method: 'POST'
            }).done(function(response){
                event.preventDefault();
                $('#boardbutton').text(`${response.title}`);
                $('.close').trigger('click');
            }).fail(function(response){
                var errorMessage = '<p>Board must have a title!</p>';
                $('.error').html(errorMessage);
            });

        });
    }

    function createBoard(){
        $('#board-modal').on('shown.bs.modal',function(event){
            var remoteUrl = $(event.relatedTarget).data('remote');
            var modal = $(this);
            $.ajax({
                method: 'get',
                url: remoteUrl
            }).done(function(response){
                modal.find('.modal-body').html(response);

                
            });
        });
    }

        $(document).on('submit','#board-form',function(event){
            event.preventDefault();
            var boardFormAction = $(this).attr('action');
            var boardData = $(this).serialize();
            
            $.ajax({
                method:'POST',
                url:boardFormAction,
                data:boardData
            }).done(function(response){
                event.preventDefault();
                window.location.href = "/board/detail/" + response.board_id
                console.log(response, 'test')
                $('.close').trigger('click');
                var owner = response.board_owner
                inviteMemberButton();

            }).fail(function(response){
                //alert('invalid input');
                var errorMessage = '<p>This field is required</p>';

                $('.error-board-create').html(errorMessage);
                

            });
        })


        
    



    function listCreate(){
        $(document).on('submit','#list-form',function(event){
            event.preventDefault();

            var listFormAction = $(this).attr('action');
            var listdata = $(this).serialize();
            console.log(listFormAction, 'listcreatetesting')
            $.ajax({
                method:'POST',
                url:listFormAction,
                data:listdata
            }).done(function(response){
                event.preventDefault()
                console.log(response, 'listcreatetesting')
                window.location.href = "/board/detail/" + response.board_id
                
            }).fail(function(response){
                var errorMessage = '<p>This field is required!</p>';
                $('.error-list-create').html(errorMessage);
            });
        })
    }

    function dragCard(){
        $('.draggable').draggable( /* {
        
            connectToSortable: ".list-section",
        } */ );
        var csrf = $('input[name="csrfmiddlewaretoken"]').val();
        //console.log(cardUrl, 'test URL');

        $('.list-section').droppable({
            
            drop:function(event, ui){
                
               var sectionID = $(this).data('id');
               console.log(sectionID, 'test section');
               console.log(event, 'test event');

               var cardID = $(event.toElement).data('id');
               var cardUrl = $(event.toElement).data('url');
               console.log(cardID,cardUrl, 'test ID,url');
                $.ajax({
                    method:'POST',
                    url:cardUrl,
                    data:{'card_id':cardID,'list_id':sectionID,'csrfmiddlewaretoken':csrf}
                }).done(function(response){
                    
                    var cardcontainer = response.list_id;
                    var cardget = $(`#list-${cardcontainer}`);

                    var cardid = response.card_id;
                    var card = $(`#cardl-${cardid}`);
                    $(this).find(cardget).html(card);
                    console.log(response, 'response test');

                    var user = response.user
                    var cardTitle = response.card_title
                    var listTitle = response.list_title
                    var activity_template = `<p class="mb-1">${user} just moved ${cardTitle} to ${listTitle}</p>
                    <small class="text-muted">Donec id elit non mi porta.</small>`
                    console.log(user, 'response user');
                    $('.list-group').find('#logContainer').append(activity_template);
                });
            }
        });
    }


    $(document).on('shown.bs.modal','#card-view-modal',function(event){
        event.preventDefault();
        var remoteUrl = $(event.relatedTarget).data('remote');
        var modal = $(this);
        var cardTitle = $(event.relatedTarget).data('title');
        $.ajax({
            
            url:remoteUrl,
            method:'GET'
            
        }).done(function(response){
            event.preventDefault();
            modal.find('.modal-body').html(response);
            modal.find('.modal-title').html(cardTitle);
            
            $(function(){
                $('[data-toggle="popover"]').popover(
                    {html:true}
                )
            });

        });


    });

  
        
        $(document).on('blur','.card-detail-title', function(){
            event.preventDefault();
            console.log(document, 'document test');
            var url = $(this).data('update');
            var oldValue = $(this).data('title');
            var newTitle = $(this).text();
            var csrf = $('input[name="csrfmiddlewaretoken"]').val();
            
           
            if(newTitle.length == 0) {
                $(this).text(oldValue);
            } else {
                $.ajax({
                    url: url,
                    method: 'POST',
                    data: {'title': newTitle, 'csrfmiddlewaretoken':csrf}
                }).done(function(response){
                    //edit card title in background
                    var cardID = response.card_id
                    var card = $(`#carddetail-${cardID}`)
                    console.log(response.title, 'respondcardqweasdas')
                    $(card).html(`${response.title}`);
                    
                    

                });
            }
        });
    




        $(document).on('blur','.card-detail-label', function(){
            var url = $(this).data('update');
            var oldValue = $(this).data('label');
            var newLabel = $(this).text();
            var csrf = $('input[name="csrfmiddlewaretoken"]').val();

            if(newLabel.length == 0){
                $(this).text(oldValue);
            } else {
                $.ajax({
                    url:url,
                    method:'POST',
                    data: {'labels': newLabel, 'csrfmiddlewaretoken':csrf}
                }).done(function(response){
                    
                    

                });
            }

        });


        
    
    function inviteMemberButton(){
        $('#board-modal').on('shown.bs.modal',function(event){
            var remoteUrl = $(event.relatedTarget).data('remote');
            var modal = $(this);
            $.ajax({

                method:'GET',
                url: remoteUrl
            }).done(function(response){
                modal.find('.modal-body').html(response);
                //inviteMemberSubmit();
            });

        })
    }

   
        $(document).on('submit','#invite-form',function(event){
            event.preventDefault();
            var inviteFormAction = $(this).attr('action');
            var inviteData = $(this).serialize();
            $.ajax({
                method: 'POST',
                url: inviteFormAction,
                data: inviteData
            }).done(function(response){
                $('.close').trigger('click');
                alert("Email invitation sent!");
                console.log(response,'invitetest')
            }).fail(function(response){
                var errorMessage = '<p style="color:red">Invalid input!</p>';
                var errorMess = '<p style="color:red">·Please check email format</p>';
                var errorMes = '<p style="color:red">·This email might be existing in a board already</p>';
                console.log(response,'invite test')
                $('.invite-success').html(errorMessage);
                $('.invite-fail').html(errorMess);
                $('.invite-failed').html(errorMes);
            });

        })


    
        $(document).on('shown.bs.modal','#card-modal',function(event){
            var remoteUrl = $(event.relatedTarget).data('remote');
            var listTitle = $(event.relatedTarget).data('title');
            var modal = $(this);

            $.ajax({
                method:'GET',
                url: remoteUrl
            }).done(function(response){
                
                modal.find('.modal-body').html(response);
                modal.find('.modal-title').html(listTitle);

                $(function () {
                    $('[data-toggle="popover"]').popover(
                        {html:true}
                    )
                });


            }).fail(function(response){
                var errorMessage = '<p>Field has no value!</p>';
                $('.invite-success').html(errorMessage);
                
            })
        });

        $(document).on('click','.archive-this-list',function(event){
            var url = $(this).data('url');
            var archiveID = $(this).data('id')
            var listSectionID = $(event.toElement).data('id')
            

            $.ajax({
                method:'GET',
                url:url
            }).done(function(response){
                
                $('.close').trigger('click');

            })
        });
    

        
        $(document).on('shown.bs.modal','#board-modal',function(event){
            var remoteUrl = $(event.relatedTarget).data('remote');
            var modal = $(this);
            var boardTitle = $(event.relatedTarget).data('title');

            $.ajax({
                method:'GET',
                url: remoteUrl
            }).done(function(response){
                console.log(response, 'responsedesdasd')
                modal.find('.modal-body').html(response);
                modal.find('.modal-title').html(boardTitle);

                $(function () {
                    $('[data-toggle="popover"]').popover(
                        {html:true}
                    )
                });

                  
            })
        })

        
        $(document).on('shown.bs.modal','#boards-view-modal', function(event){
            var remoteUrl = $(event.relatedTarget).data('remote');
            var modal = $(this);

            $.ajax({
                method:'GET',
                url:remoteUrl
            }).done(function(response){
                modal.find('.modal-body').html(response);
            })

        })


        $(document).on('click','.delete-board-butt', function(){
            var archivedBoard = $('.list-of-archived-boards');
            var url = $(this).data('url');

            $.ajax({
                method:'GET',
                url:url
            }).done(function(response){
                
                var boardID = response.boardID
                var archived = $(`#board-${boardID}`)
                console.log(archived,"testing board id")
                var template = '<p>Board deleted</p>'
                $('.listsofarchvied').find(archived).html(template);   
            })
        })


        $(document).on('click','.retrieve-board-butt',function(){
            var retrieveBoard = $('.list-of-archived-boards');
            var url = $(this).data('url');

            $.ajax({
                method:'GET',
                url:url
            }).done(function(response){
                console.log(response,'archive response blabla')
                var boardID = $(`#board-${response.board_id}`)
                var template = '<p>Board restored</p>'
                
                $('.listsofarchvied').find(boardID).html(template)
            })
        })



        $(document).on('click','.retrieve-list-butt',function(){
            var url = $(this).data('url');

            $.ajax({
                method:'GET',
                url: url
            }).done(function(response){
                var retrieve_template= '<p> List is retrieved! </p>'
                var archived_list = $(`#list-${response.blist_id}`);

                $('.lists-of-archived-lists').find(archived_list).html(retrieve_template);
                $('.close').trigger('click');
                window.location.href = "/board/detail/" + response.board_id
            })
        })

        $(document).on('click','.delete-list-butt',function(){
            var url = $(this).data('url');
            $.ajax({
                    method:'GET',
                    url:url
                }).done(function(response){
                    console.log(response,'retrieve test')
                    var listID = response.blist_id
                    var retrieve_template = '<p>List is deleted!</p>'
                    var archived_list = $(`#list-${listID}`);
                    
                    $('.lists-of-archived-lists').find(archived_list).html(retrieve_template);
            });        

        })


        $(document).on('click','.retrieve-card-butt', function(){
            var url = $(this).data('url');

            $.ajax({
                method:'GET',
                url: url
            }).done(function(response){
                var retrieve_template= '<p> Card is retrieved! </p>'
                var archived_list = $(`#card-${response.card_id}`);

                $('.lists-of-archived-cards').find(archived_list).html(retrieve_template);
                $('.close').trigger('click');
                window.location.href = "/board/detail/" + response.board_id
            })
        })


        $(document).on('click','.delete-card-butt', function(){
            var url = $(this).data('url');

            $.ajax({
                method:'GET',
                url: url
            }).done(function(response){
                var retrieve_template= '<p> Card deleted! </p>'
                var archived_list = $(`#card-${response.card_id}`);

                $('.lists-of-archived-cards').find(archived_list).html(retrieve_template);
                $('.close').trigger('click');
                window.location.href = "/board/detail/" + response.board_id
            })
        })




        

});

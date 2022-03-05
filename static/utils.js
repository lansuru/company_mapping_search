// This needs to agree with MAX_NUM_RESULTS defined in wsgi.py.
var MAX_NUM_RESULTS = 20;


function searchAndFilter() {
  var input= $('#search-input').val().trim();
  var regex = new RegExp(input, 'i');

  //searchAndFilter.trs represent the whole table
  //initiate the table only once
  if (typeof searchAndFilter.trs == 'undefined') {
    // gt(0): skip the first <tr> in <thead>...</thead>
    searchAndFilter.trs =$('#mapping-table tr:gt(0)');
  }

  //when this function is called, we hide the whole table
  //either show filtered result, or blank
  searchAndFilter.trs.hide();

  //get searchmode, do the search/filter
  var searchmode = $('#search-mode input[name=searchModeBtn]:checked').val();
  var matched_trs;

  if (searchmode === 'legacy') {
    matched_trs = searchAndFilter.trs.filter(function() {
      return regex.test($(this).find('td').eq(0).text())
    });
  } else if (searchmode === 'new') {
    matched_trs = searchAndFilter.trs.filter(function() {
      return regex.test($(this).find('td').eq(1).text())
    });
  } else {
    matched_trs = searchAndFilter.trs.filter(function() {
      return regex.test($(this).find('td').eq(0).text()) ||
             regex.test($(this).find('td').eq(1).text())
    });
  }

  //after the search, show first 20 result
  matched_trs.slice(0, MAX_NUM_RESULTS).show();

  //if result length > 25, show the msg
  $('#note-hidden-results').css('display',
      (matched_trs.length > MAX_NUM_RESULTS) ? '' : 'none');

  //call showNoResultsMsg function
  if (matched_trs.length === 0) {
    showNoResultsMsg(searchmode)
  } else {
    $('#note-no-results').html("");
  }

}

function showNoResultsMsg(searchmode) {
  var noresults = '<em>Sorry, no match found';

  if (searchmode === 'legacy') {
    noresults += ' in <strong>Legacy Codes</strong>. Try searching in <strong>New Codes</strong>.</em>';
  } else if (searchmode === 'new') {
    noresults += ' in <strong>New Codes</strong>. Try searching in <strong>Legacy Codes</strong>.</em>';
  } else {
    noresults += ' in both <strong>Legacy Codes</strong> and <strong>new Codes</strong>.</em>';
  }

  //insert the msg to note-no-results <p> tag
  $('#note-no-results').html(noresults);
}

function resetInput(event) {
  if (event.key === 'Escape') {
    document.getElementById('search-input').value = '';
  }
}

//various event to trigger calling of the functions above
$('#search-input').keyup((event) => {
  resetInput(event);
  searchAndFilter();
});

$('#search-mode input[name=searchModeBtn]').change(searchAndFilter);

$('#show-all').click(() => {
  MAX_NUM_RESULTS = 99999;
  searchAndFilter();
});


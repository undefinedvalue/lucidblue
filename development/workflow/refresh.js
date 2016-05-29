// Included in all pages when running the development server
// Will auto-refresh the page when it has been modified on the server

var checkModified = function(originalMTime) {
  var xhr = new XMLHttpRequest();

  xhr.open('HEAD', window.location.href, true);

  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
      var mtime = new Date(xhr.getResponseHeader('Last-Modified'));
      if (mtime.toString() !== 'Invalid Date') {
        if (originalMTime && mtime.toString() !== originalMTime.toString()) {
          location.reload(true);
        } else {
          originalMTime = mtime;
        }
      }

      setTimeout(function() { checkModified(originalMTime); }, 600);
    }
  }

  xhr.send();
};

checkModified()


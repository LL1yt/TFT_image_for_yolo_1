$(document).ready(function () {
    $('#sidebar-toggle').click(function () {
        $('#sidebar').toggleClass('active');
        // Adjust the content area based on the sidebar state
        $('#content').toggleClass('active');
    });
});

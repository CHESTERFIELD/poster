function BackToTop(){
  let button = $(".arrow-top");
  console.log(button);

  $(window).on('scroll', () => {
    if($(this).scrollTop() >= 530) {
      button.fadeIn(300);
    } else {
      button.fadeOut(300);
    }
  });
  button.on('click', (e) => {
    e.preventDefault();
    $('html').animate({scrollTop: 0}, 1500);
  })
}

BackToTop();

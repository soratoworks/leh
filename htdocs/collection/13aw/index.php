<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>LEH -2013 Collection Spring / Summer-</title>
<meta name="robots" content="index,follow" />
<meta name="keywords" content="LEH" />
<meta name="description" content="The official website of Leh" />
<link href="../../css/style.css" rel="stylesheet" type="text/css" media="all" />
<link href="../../css/css_white.css" rel="stylesheet" type="text/css" media="all" />
<link href="../../css/menu.css" rel="stylesheet" type="text/css" media="all" />

<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>
<script type="text/javascript">
$(document).ready(function()
{
  //change_thumb
  $(function(){
    $('.thumb_img a').click(function(){
      var h = $(this).eq(0).attr('rel');
      $('.main_img img').fadeOut(function(){
        ($('.main_img img').attr("src",h)).fadeIn();
      });
      return false;
    })
  });
  
  });
</script>

</head>

<body>


<!--全体の囲みここから-->
<div id="wrapper_collection_img_13ss">


<!-- menuここから -->
	<div id="menu_13ss_collection_index">
		<?php
			include "../../menu_collection.php";
		?>
	</div>



<!--Collectionイメージここから-->

	<div id="collection_img_13ss">

		<div class="collection_arrow_13ss">
			<a href="../../collection.php" class="imghover">
				<img src="../../images/collection/13ss/arrow_left_13ss.jpg" alt="BACK" border="0" />
			</a>
		</div>
		
		<div id="collection_img_13ss_space">
			<div class="thumb_img">
			
			<div class="collection_img_01_13ss">
				<a href="#" rel="../../images/collection/13ss/img_01.jpg">
				<img src="../../images/collection/13ss/img_01.jpg" width="80" />
				</a>
			</div>

			<div class="collection_img_01_13ss">
				<img src="../../images/collection/13ss/img_02.jpg" width="80" />
			</div>

			<div class="collection_img_01_13ss">
				<a href="#" rel="../../images/collection/13ss/img_03.jpg">
				<img src="../../images/collection/13ss/img_03.jpg" width="80" />
				</a>
			</div>

			<div class="collection_img_01_13ss">
				<a href="#" rel="../../images/collection/13ss/img_04.jpg">
				<img src="../../images/collection/13ss/img_04.jpg" width="80" />
				</a>
			</div>

			<div class="collection_img_01_13ss">
				<a href="#" rel="../../images/collection/13ss/img_05.jpg">
				<img src="../../images/collection/13ss/img_05.jpg" width="80" />
				</a>
			</div>

			<div class="collection_img_01_13ss">
				<a href="#" rel="../../images/collection/13ss/img_06.jpg">
				<img src="../../images/collection/13ss/img_06.jpg" width="80" />
				</a>
			</div>

			<div class="collection_img_01_13ss">
				<img src="../../images/collection/13ss/img_07.jpg" width="80" />
			</div>

			<div class="collection_img_01_13ss">
				<a href="#" rel="../../images/collection/13ss/img_08.jpg">
				<img src="../../images/collection/13ss/img_08.jpg" width="80" />
				</a>
			</div>

			<div class="collection_img_01_13ss">
				<a href="#" rel="../../images/collection/13ss/img_09.jpg">
				<img src="../../images/collection/13ss/img_09.jpg" width="80" />
				</a>
			</div>

			<div class="collection_img_01_13ss">
				<a href="#" rel="../../images/collection/13ss/img_10.jpg">
				<img src="../../images/collection/13ss/img_10.jpg" width="80" />
				</a>
			</div>

			<div class="collection_img_01_13ss">
				<a href="#" rel="../../images/collection/13ss/img_11.jpg">
				<img src="../../images/collection/13ss/img_11.jpg" width="80" />
				</a>
			</div>

			<div class="collection_img_01_13ss">
				<a href="#" rel="../../images/collection/13ss/img_12.jpg">
				<img src="../../images/collection/13ss/img_12.jpg" width="80" />
				</a>
			</div>
			
			</div>
		</div> <!-- /collection_img_13ss_space -->
		
		
		<div id="collection_img_13ss_zoom_space">
			<div class="main_img">
				<img src="../../images/collection/13ss/img_01.jpg" />
			</div>
		</div> <!-- /collection_img_13ss_zoom_space -->
		
		<div class="collection_arrow_13ss">
			<a href="item/01.php" class="imghover">
				<img src="../../images/collection/13ss/arrow_right_13ss.jpg" alt="NEXT" border="0" />
			</a>
		</div>
		
	</div>

	</div>

<!--各ページへのリンクここまで-->

	<br clear="all">

<!--FOOTERここから-->

    <div id="footer">
        Copyright (C) All Rights Reserved by Leh.<br />
        <span class="company_name"><a href="../../index.html">www.leh.jp</a></span><br /><br />
		<a href="mailto:info@leh.jp"><img src="../../img/mail.jpg" alt="LEHにメール" width="18" height="12" border="0" /></a>
    </div>

<!--FOOTERここまで-->

</div>
<!--全体の囲みここまで-->

<!--   解析用  -->
		<?php
			include "../../analyze.php";
		?>
<!--   解析用  -->

</body>
</html>

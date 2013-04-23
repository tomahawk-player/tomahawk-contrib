<?php
/*
Plugin Name: Tomahk shortcodes
Description: Use shortcodes to embed playlists, albums and single tracks from toma.hk.
Version: 0.1
Author: G.Breant
Author URI: http://pencil2d.org
Plugin URI: http://wordpress.org/extend/plugins/tomahk-shortcodes
License: GPL2
*/

class tomahk_shortcodes {
    
	/** Paths *****************************************************************/

	public $file = '';
	
	/**
	 * @public string Basename of the plugin directory
	 */
	public $basename = '';

	/**
	 * @public string Absolute path to the plugin directory
	 */
	public $plugin_dir = '';

	private static $instance;

	public static function instance() {
		if ( ! isset( self::$instance ) ) {
			self::$instance = new tomahk_shortcodes;
			self::$instance->setup_globals();
			self::$instance->includes();
			self::$instance->setup_actions();
		}
		return self::$instance;
	}
        
	/**
	 * A dummy constructor to prevent it from being loaded more than once.
	 *
	 * @since bbPress (r2464)
	 * @see bbPress::instance()
	 * @see bbpress();
	 */
	private function __construct() { /* Do nothing here */ }
        
	function setup_globals() {

		/** Paths *************************************************************/
		$this->file       = __FILE__;
		$this->basename   = plugin_basename( $this->file );
		$this->plugin_dir = plugin_dir_path( $this->file );
		$this->plugin_url = plugin_dir_url ( $this->file );

	}
        
	function includes(){
	}
	
	function setup_actions(){            
            add_shortcode( 'twk-playlist', array($this, 'shortcode_playlist' ));
            add_shortcode( 'twk-track', array($this, 'shortcode_track' ));
            add_shortcode( 'twk-album', array($this, 'shortcode_album' ));

	}

        function shortcode_playlist( $args , $item_url = null) {

            // Attributes
            extract( shortcode_atts(
                    array(
                    ), $args )
            );
            
            $item = new tomahk_Playlist($item_url, $args);
            return $item->render();
        }
        
        function shortcode_track( $args , $item_args = null) {

            // Attributes
            extract( shortcode_atts(
                    array(
                    ), $args )
            );
            
            //Artist
            if($args['artist']){
                $item_args['artist']=$args['artist'];
                unset($args['artist']);
            }
            
            //Title
            if($args['title']){
                $item_args['title']=$args['title'];
                unset($args['title']);
            }
            
            $item = new tomahk_Track($item_args, $args);
            return $item->render();
        }
        
        function shortcode_album( $args , $item_args = null) {

            // Attributes
            extract( shortcode_atts(
                    array(
                    ), $args )
            );
            
            //Artist
            if($args['artist']){
                $item_args['artist']=$args['artist'];
                unset($args['artist']);
            }
            
            //Title
            if($args['title']){
                $item_args['title']=$args['title'];
                unset($args['title']);
            }

            $item = new tomahk_Album($item_args, $args);
            return $item->render();
        }

        function extract_url($tomahawk_url){
            
            //remove arguments
            $tomahawk_url = strtok($tomahawk_url, '?');
            
            $matches = array();
            $pattern = "#^https?://([a-z0-9-]+\.)*toma\.hk(/.*)?$#";
            
            preg_match($pattern,$tomahawk_url, $matches);

            if (!isset($matches[2])) return false;
            
            $suffix = $matches[2];
            $suffix = ltrim($suffix, '/');
            return $suffix;

        }
        
        function validate_tomahk_id($id){
            if (!ctype_alnum($id)) return false;
            return $id;
        }

}

class tomahk_Playlist {
    
    var $tomahk_id = null;
    var $width;
    var $height;
    
    function __construct($playlist_url,$style_args=false){
        
        if (!$playlist_url) return false;
        
        //STYLE
        $style_default_args = array(
            'width'=>550, 
            'height'=>430,
        );
        
        $style_args = wp_parse_args($style_args,$style_default_args);
        
        foreach($style_default_args as $key=>$arg){
            $this->$key = $style_args[$key];
        }
        
        //PLAYLIST
        $playlist_default_args=array(
            'tomahk_id'=>null
        );
        
        $playlist_args = $this->extract_url_info($playlist_url);
        
        $playlist_args = wp_parse_args($playlist_args,$playlist_default_args);

        foreach($playlist_args as $key=>$arg){
            $this->$key = $arg;
        }
    }
    
    function extract_url_info($url){
        //get URL suffix
        $suffix = tomahk_shortcodes::extract_url($url);
        
        $playlist_arr=explode('p/',$suffix);
        
        if (!isset($playlist_arr[1])) return false;
        
        $args['tomahk_id'] = tomahk_shortcodes::validate_tomahk_id($playlist_arr[1]);

        return $args;
    }
    
    function render(){
        if (!$this->tomahk_id) return false;
        
        $url = 'http://toma.hk/p/'.$this->tomahk_id;
        $url_args['embed'] = 'true';
        $url = add_query_arg($url_args,$url);
        
        ob_start();
        ?>
        <iframe src="<?php echo $url;?>" width="<?php echo $this->width;?>" height="<?php echo $this->height;?>" scrolling="no" frameborder="0" allowtransparency="true" ></iframe>
        <?php
        $iframe = ob_get_contents();
        ob_end_clean();
        return $iframe;
    }
}

class tomahk_Track {
    
    var $tomahk_id = null;
    var $artist;
    var $title;
    var $disabled_resolvers=array();
    var $autoplay;
    var $width;
    var $height;
    
    function __construct($track_args=false,$style_args=false){

        //style args
        $style_default_args = array(
            'width'=>200, 
            'height'=>200,
            'autoplay'=>false,
            'disabled_resolvers'=>null
        );
        //track args
        $track_default_args = array(
            'tomahk_id'=>false,
            'artist'=>false,
            'title'=>false
        );
        
        $style_args = wp_parse_args($style_args,(array)$style_default_args);
        
        foreach($style_default_args as $key=>$arg){
            $this->$key = $style_args[$key];
        }
        
        //check for a toma.hk url
        if ((isset($track_args))&&(is_string($track_args))){
            $track_args = $this->extract_url_info($track_args);
        }
        
        $track_args = wp_parse_args((array)$track_args,$track_default_args);

        foreach($track_default_args as $key=>$arg){
            $this->$key = $track_args[$key];
        }
    }
    
    function extract_url_info($url){
        
        $args = array();
        
        //get URL suffix
        $suffix = tomahk_shortcodes::extract_url($url);
        $args['tomahk_id'] = tomahk_shortcodes::validate_tomahk_id($suffix);
        
        if ($args['tomahk_id']){
            $json = file_get_contents('http://www.toma.hk/api.php?id='.$args['tomahk_id']);
            $api_args = json_decode($json,true);
            $args = array_merge($api_args,$args);
        }

        return $args;
    }

    
    function render(){
        if ((!$this->artist)||(!$this->title)) return false;
        
        $url = 'http://toma.hk/embed.php';
        
        $url_args['artist'] = $this->artist;
        $url_args['title'] = $this->title;
        $url_args['autoplay'] = ($this->autoplay) ? 'true' : 'false';
        
        $disabled_resolvers_str = implode(',',(array)$this->disabled_resolvers);
        
        if ($disabled_resolvers_str)
            $url_args['disabledResolvers'] = $disabled_resolvers_str;
        
        $url = add_query_arg($url_args,$url);

        ob_start();
        ?>
        <iframe src="<?php echo $url;?>" width="<?php echo $this->width;?>" height="<?php echo $this->height;?>" scrolling="no" frameborder="0" allowtransparency="true" ></iframe>
        <?php
        $iframe = ob_get_contents();
        ob_end_clean();
        return $iframe;
    }
}

class tomahk_Album {

    var $artist;
    var $title;
    var $width;
    var $height;
    
    function __construct($album_args=false,$style_args=false){

        //style args
        $style_default_args = array(
            'width'=>550, 
            'height'=>430,
            'artist'=>null,
            'title'=>null
        );
        
        //album args
        $album_default_args = array(
            'artist'=>false,
            'title'=>false
        );
        
        $style_args = wp_parse_args($style_args,$style_default_args);

        foreach($style_default_args as $key=>$arg){
            $this->$key = $style_args[$key];
        }

        //check for a toma.hk url
        if (isset($album_args)&&is_string($album_args)){
            $album_args = $this->extract_url_info($album_args);
        }
        
        $album_args = wp_parse_args($album_args,$album_default_args);

        foreach($album_default_args as $key=>$arg){
            $this->$key = $album_args[$key];
        }

    }
    
    function extract_url_info($url){

        $args = array();
        
        //get URL suffix
        $suffix = tomahk_shortcodes::extract_url($url);
        
        $album_arr=explode('album/',$suffix);
        
        if (!isset($album_arr[1])) return false;
        
        $albuminfo = explode('/',$album_arr[1]);
        
        if(count($albuminfo)<2)return false;
        
        $args['artist']= urldecode($albuminfo[0]);
        $args['title']= urldecode($albuminfo[1]);

        return $args;
    }
    
    function render(){
        if ((!$this->artist)||(!$this->title)) return false;
        
        $url = 'http://toma.hk/album/'.$this->artist.'/'.$this->title;
        $url_args['embed'] = 'true';
        $url = add_query_arg($url_args,$url);
        
        ob_start();
        ?>
        <iframe src="<?php echo $url;?>" width="<?php echo $this->width;?>" height="<?php echo $this->height;?>" scrolling="no" frameborder="0" allowtransparency="true" ></iframe>
        <?php
        
        $iframe = ob_get_contents();
        ob_end_clean();
        return $iframe;
    }
}





/**
 * The main function responsible for returning the one true bbPress Instance
 * to functions everywhere.
 *
 * Use this function like you would a global variable, except without needing
 * to declare the global.
 *
 *
 * @return The one true Instance
 */

function tomahk_shortcodes() {
	return tomahk_shortcodes::instance();
}

tomahk_shortcodes();


?>
package com.roguebloodmoon.prototype;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.Locale;

public class MainActivity extends Activity {
    private WebView web;
    private static final String HOST = "rogue.local";

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        immersive();
        web = new WebView(this);
        web.setBackgroundColor(0xff090d10);
        web.getSettings().setJavaScriptEnabled(true);
        web.getSettings().setDomStorageEnabled(true);
        web.getSettings().setAllowFileAccess(false);
        web.getSettings().setAllowContentAccess(false);
        web.getSettings().setMediaPlaybackRequiresUserGesture(true);
        web.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return !HOST.equals(request.getUrl().getHost());
            }
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest req) {
                String path = req.getUrl().getPath();
                if (!HOST.equals(req.getUrl().getHost()) || path == null || path.contains("..")) return denied();
                path = path.equals("/") ? "index.html" : path.substring(1);
                String mime = "application/octet-stream";
                String lower = path.toLowerCase(Locale.ROOT);
                if (lower.endsWith(".html")) mime = "text/html";
                else if (lower.endsWith(".css")) mime = "text/css";
                else if (lower.endsWith(".js")) mime = "application/javascript";
                else if (lower.endsWith(".jpg")) mime = "image/jpeg";
                else if (lower.endsWith(".png")) mime = "image/png";
                else if (lower.endsWith(".wav")) mime = "audio/wav";
                else if (lower.endsWith(".mp3")) mime = "audio/mpeg";
                else if (lower.endsWith(".mp4")) mime = "video/mp4";
                try { return new WebResourceResponse(mime, "UTF-8", getAssets().open(path)); }
                catch (IOException e) { return denied(); }
            }
        });
        setContentView(web);
        web.loadUrl("https://" + HOST + "/index.html");
    }
    private WebResourceResponse denied() {
        return new WebResourceResponse("text/plain", "UTF-8", 404, "Not Found", null, new ByteArrayInputStream(new byte[0]));
    }
    private void immersive() {
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN
            | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
    }
    @Override public void onWindowFocusChanged(boolean focus) { super.onWindowFocusChanged(focus); if (focus) immersive(); }
    @Override protected void onPause() { if (web != null) { web.evaluateJavascript("window.pauseApp && window.pauseApp()", null); web.onPause(); } super.onPause(); }
    @Override protected void onResume() { super.onResume(); if (web != null) web.onResume(); }
    @Override public void onBackPressed() { web.evaluateJavascript("window.goBack && window.goBack()", null); }
    @Override protected void onDestroy() { if (web != null) { web.destroy(); web = null; } super.onDestroy(); }
}

package org.odk.collect.android.activities;

import org.odk.collect.android.R;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

public class AuthenticateScreen extends Activity {

	public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        setContentView(R.layout.authenticate_screen);
        ((Button)findViewById(R.id.authenticate_button)).setOnClickListener(login);
	}
	
	private OnClickListener login = new OnClickListener() {
		@Override
		public void onClick(View v) {
			String username = ((EditText)findViewById(R.id.authenticate_username)).getText().toString();
			String password = ((EditText)findViewById(R.id.authenticate_password)).getText().toString();
			
			if (username.equals("") || password.equals("")) //Break out if no user name or password is given
				return; 
			
			if (username.equals("test") && password.equals("1234")) //Check credentials then proceed to ODK-Collect
			{
				startMain();
				//Todo: proper authentication
			}
			else { //Incorrect Password
				Toast.makeText(AuthenticateScreen.this, "Incorrect user name and password combination", Toast.LENGTH_SHORT).show();
			}
		}
	};
	
	private void startMain() {
        // launch new activity and close authentication screen
        startActivity(new Intent(AuthenticateScreen.this, MainMenuActivity.class));
        finish();
    }
}

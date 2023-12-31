```
/
/ tarot /                           # URL-prefix or subdomain TBD

        / login                     # Only pages accessible if not logged in,
        / signup                      not accessible if logged in

        / menu                      # Automatic redirect after login or 404.
                                      Possibility to join or create a game

        / match / <match_id>        # Where you play the game
                        / debug     # Access only for admins, ability to see
                                      data about game

        / user  / <user_id>         # Page to see stats and public profiles 
                                      of players

        / settings                  # Customization of site appearance and
                                      profile settings and in-game settings
```
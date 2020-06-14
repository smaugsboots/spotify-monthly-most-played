from favourites import *

print('\n\nspotify-monthly-most-played by Sameer Aggarwal\n______________________________________________\n')


def main():

    token = get_token()
    history = get_streamings()
    sorted_history = sort_into_months(history)
    avail_months = list(sorted_history.keys())
    
    print('\nStreaming history was found for the following months:') 
    print(avail_months)
    print('')

    while True:
        month = str(input('Choose a month to get your played tracks for: '))
        if month not in avail_months:
            print("\nSorry, that's not a valid month.")
            continue
        else:
            print('\nCreating playlists (beep boop) ...\nPlease allow around 5 minutes (!)\n')
            break

    start = time.time()
    consolidated_history = consolidate_streams(sorted_history, month, token)
    counter = create_playlists(consolidated_history, 25, token)
    time_taken = time.time() - start
    print('Done! %d playlist(s) created.' % counter)
    print('------- %f seconds -------\n' % time_taken)

    while True:
        choice = input('Would you like a CSV with most played data for ' + month + ' created? (y/n): ')
        if choice == 'y':
            print('\nCreating CSV (beep boop) ...\n')
            top_tracks(month, consolidated_history)
            break
        elif choice == 'n':
            print('')
            break
        else:
            print("\nSorry, that's not a valid choice.")
            continue
    
    while True:
        run_again = input('Would you like to get your most played tracks for another month? (y/n): ')
        if run_again == 'y' or run_again == 'n':
            break
        else:
            print("\nSorry, that's not a valid choice.")
            continue
    
    if run_again == 'y':
        main()
    else:
        print('\nThank you for using spotify-monthly-most-played.\n')


if __name__ == "__main__":
    main()
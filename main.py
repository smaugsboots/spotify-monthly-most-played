import favourites as fav
import time


def main():

    token = fav.get_token()
    sorted_history = fav.sort_into_months(history)
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
            print('\n* * *\n')
            break

    while True:
        try:
            num_tracks = int(input('Choose how many tracks you want included in each playlist (25 is a good default): '))
        except ValueError:
            print("\nSorry, that's not a valid response. Please enter an integer.")
            continue
        if num_tracks <= 0:
            print("\nSorry, that's not a valid response. Please enter an integer greater than 0.")
        else:
            print('\n* * *\n\nCreating playlists (beep boop) ...\nPlease allow around 5 minutes (!)\n')
            break

    start = time.time()
    consolidated_history = fav.consolidate_streams(sorted_history, month, token)
    counter = fav.create_playlists(consolidated_history, num_tracks, token)
    time_taken = time.time() - start
    print('Done! %d playlist(s) created.' % counter)
    print('------- %f seconds -------\n\n* * *\n' % time_taken)

    while True:
        choice = input('Would you like a CSV with info about your most played tracks for ' + month + ' created? (y/n): ')
        if choice == 'y':
            print('\n* * *\n\nCreating CSV (beep boop) ...\n')
            fav.top_tracks(month, path, consolidated_history)
            print('* * *\n')
            break
        elif choice == 'n':
            print('\n* * *\n')
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
        print('\n* * * * * * *')
        main()
    else:
        print('\n______________________________________________\n\nThank you for using spotify-monthly-most-played.\n')


if __name__ == "__main__":

    print('\n\nspotify-monthly-most-played by Sameer Aggarwal\n______________________________________________\n')
    input('Press ENTER to continue...\n')
    print('* * * * * * *\n')

    while True:
        pathstring = input("Enter the path (absolute or relative) for the directory where your streaming history is located \
(the files will be JSON files with the name format 'StreamingHistoryX'):\n")
        path = ''
        for i in pathstring:
            if i == '\\':
                path += '/'
            else:
                path += i
        try:
            history = fav.get_streamings(path)
            if len(history) == 0:
                print("\nSorry, that's not a valid response. Please enter the correct path.")
                continue
            else:
                print('\n* * * * * * *')
                break
        except FileNotFoundError:
            print("\nSorry, that's not a valid response. Please enter a valid path.")
            continue

    main()
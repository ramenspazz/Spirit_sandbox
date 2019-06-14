# Spirit_sandbox
The first required step to use this Sandbox is to install spirit. To install spirit from the release - or any branch if you so choose, first ensure that you have these dependencies (this setup instruction assumes you are running Linux):
git and cmake

Run:

git clone https://github.com/spirit-code/spirit.git

to download from the release branch. If you want to download from the devlopment branch which has more support for our purposes, use instead:

git clone --branch develop https://github.com/spirit-code/spirit.git

Once this is done, set directory to the downloaded location of the git clone and run in this order:

./clean.sh # to ensure clean install. Optional
./cmake.sh # to generate a cmake file to be used in compiling your module/library
./make.sh -jN # where N is the number of threads that you can run at one time at most, and as many as you feel like at least

After this, the module needs to be added into python so that it can be used. To do this, run:

python -m pip install -e /path/to/spirit/core/python/

sometimes you may need to add --your_username to the flags inorder to properly set permission

And then you should be good to go with spirit.

Further instructions incoming!

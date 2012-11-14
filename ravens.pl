#!/usr/bin/perl
#
# ravens.pl
#




use strict;
use warnings;
use HTML::TreeBuilder::XPath;
use WWW::Curl::Easy;
use DBI;
use Time::Local;

my $earliest_date = '2011-09-01 00:00:00';

my $dbh = DBI->connect('dbi:mysql:dbname=FanForums', 'root','abc');
my $sth = $dbh->prepare("INSERT INTO posts(forum, thread, user, post_time, post_content) VALUES(?,?,?,?,?);");

my $forum = 'Baltimore Ravens Official';

sub timeformat {
	my ($datetime) = (@_);
	substr($datetime, 10, 1) = ' ';
	return substr($datetime, 0, 19);
}

sub download {
	my ($url, $store) = @_;
	my $curl = WWW::Curl::Easy->new();
	$curl->setopt(CURLOPT_HEADER, 1);
	$curl->setopt(CURLOPT_URL, $url);
	$curl->setopt(CURLOPT_WRITEDATA, $store);
	my $retcode = $curl->perform();
	if ($retcode != 0) {
		printf "Error occurred while downloading: $retcode: " . $curl->strerror($retcode) . ' ' . $curl->errbuf. "\n";
		printf "url: $url\n";
		return 0;
	}
	return 1;
}

sub parse {
	my ($data, $xpath, $attr) = @_;
	my $parser = HTML::TreeBuilder::XPath->new();
	$parser->parse($data);

	return map {$_->{$attr}} $parser->findnodes($xpath);
}

sub thread {
	my ($threadurl, $url) = @_;
	my $data;
	download($url, \$data);
	my $parser = HTML::TreeBuilder::XPath->new();
	$parser->parse($data);
	my @users = $parser->findvalues('//div[@class="post_wrap"]/h3/span/a[@hovercard-ref="member"]');
	my @dates = map {timeformat($_->{'title'})} $parser->findnodes('//div[@class="post_body"]/p/abbr');
	my @posts = $parser->findvalues('//div[@class="post_body"]/div');
	my @next_page = parse($data, '//ul/li[@class="next"]/a', 'href');
	foreach my $i (0..$#users) {
		if ($dates[$i] ge $earliest_date) {
			$sth->execute($forum, $threadurl, $users[$i], $dates[$i], $posts[$i]);
		}
	}
	thread($threadurl, $next_page[0]) unless (@next_page == 0);
}

sub forum {
	my ($url) = @_;
	my $data;
	download($url, \$data);
	my @threads = parse($data, '//td/h4/a[@class="topic_title"]', 'href');
	my @next_page = parse($data, '//ul/li[@class="next"]/a', 'href');
	for (@threads) {
		thread($_, $_);
	}
	forum($next_page[0]) unless (@next_page == 0);
}

my $url = 'http://boards.baltimoreravens.com';
my $store;
download($url, \$store) || die "Could not download \'$url\'";
my @forums = parse($store, '//div/div/div/div/div/table/tr/td/h4/a', 'href');

for (@forums) {
	forum($_);
}

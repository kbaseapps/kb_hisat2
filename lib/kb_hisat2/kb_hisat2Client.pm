package kb_hisat2::kb_hisat2Client;

use JSON::RPC::Client;
use POSIX;
use strict;
use Data::Dumper;
use URI;
use Bio::KBase::Exceptions;
my $get_time = sub { time, 0 };
eval {
    require Time::HiRes;
    $get_time = sub { Time::HiRes::gettimeofday() };
};

use Bio::KBase::AuthToken;

# Client version should match Impl version
# This is a Semantic Version number,
# http://semver.org
our $VERSION = "0.1.0";

=head1 NAME

kb_hisat2::kb_hisat2Client

=head1 DESCRIPTION


A KBase module: kb_hisat2
This sample module contains one small method - filter_contigs.


=cut

sub new
{
    my($class, $url, @args) = @_;
    

    my $self = {
	client => kb_hisat2::kb_hisat2Client::RpcClient->new,
	url => $url,
	headers => [],
    };

    chomp($self->{hostname} = `hostname`);
    $self->{hostname} ||= 'unknown-host';

    #
    # Set up for propagating KBRPC_TAG and KBRPC_METADATA environment variables through
    # to invoked services. If these values are not set, we create a new tag
    # and a metadata field with basic information about the invoking script.
    #
    if ($ENV{KBRPC_TAG})
    {
	$self->{kbrpc_tag} = $ENV{KBRPC_TAG};
    }
    else
    {
	my ($t, $us) = &$get_time();
	$us = sprintf("%06d", $us);
	my $ts = strftime("%Y-%m-%dT%H:%M:%S.${us}Z", gmtime $t);
	$self->{kbrpc_tag} = "C:$0:$self->{hostname}:$$:$ts";
    }
    push(@{$self->{headers}}, 'Kbrpc-Tag', $self->{kbrpc_tag});

    if ($ENV{KBRPC_METADATA})
    {
	$self->{kbrpc_metadata} = $ENV{KBRPC_METADATA};
	push(@{$self->{headers}}, 'Kbrpc-Metadata', $self->{kbrpc_metadata});
    }

    if ($ENV{KBRPC_ERROR_DEST})
    {
	$self->{kbrpc_error_dest} = $ENV{KBRPC_ERROR_DEST};
	push(@{$self->{headers}}, 'Kbrpc-Errordest', $self->{kbrpc_error_dest});
    }

    #
    # This module requires authentication.
    #
    # We create an auth token, passing through the arguments that we were (hopefully) given.

    {
	my %arg_hash2 = @args;
	if (exists $arg_hash2{"token"}) {
	    $self->{token} = $arg_hash2{"token"};
	} elsif (exists $arg_hash2{"user_id"}) {
	    my $token = Bio::KBase::AuthToken->new(@args);
	    if (!$token->error_message) {
	        $self->{token} = $token->token;
	    }
	}
	
	if (exists $self->{token})
	{
	    $self->{client}->{token} = $self->{token};
	}
    }

    my $ua = $self->{client}->ua;	 
    my $timeout = $ENV{CDMI_TIMEOUT} || (30 * 60);	 
    $ua->timeout($timeout);
    bless $self, $class;
    #    $self->_validate_version();
    return $self;
}




=head2 run_hisat2

  $return = $obj->run_hisat2($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a kb_hisat2.Hisat2Params
$return is a kb_hisat2.ResultsToReport
Hisat2Params is a reference to a hash where the following keys are defined:
	ws_name has a value which is a string
	alignmentset_name has a value which is a string
	sampleset_ref has a value which is a string
	genome_ref has a value which is a string
	num_threads has a value which is an int
	quality_score has a value which is a string
	skip has a value which is an int
	trim3 has a value which is an int
	trim5 has a value which is an int
	np has a value which is an int
	minins has a value which is an int
	maxins has a value which is an int
	orientation has a value which is a string
	min_intron_length has a value which is an int
	max_intron_length has a value which is an int
	no_spliced_alignment has a value which is a kb_hisat2.bool
	transcriptome_mapping_only has a value which is a kb_hisat2.bool
	tailor_alignments has a value which is a string
bool is an int
ResultsToReport is a reference to a hash where the following keys are defined:
	report_name has a value which is a string
	report_ref has a value which is a string

</pre>

=end html

=begin text

$params is a kb_hisat2.Hisat2Params
$return is a kb_hisat2.ResultsToReport
Hisat2Params is a reference to a hash where the following keys are defined:
	ws_name has a value which is a string
	alignmentset_name has a value which is a string
	sampleset_ref has a value which is a string
	genome_ref has a value which is a string
	num_threads has a value which is an int
	quality_score has a value which is a string
	skip has a value which is an int
	trim3 has a value which is an int
	trim5 has a value which is an int
	np has a value which is an int
	minins has a value which is an int
	maxins has a value which is an int
	orientation has a value which is a string
	min_intron_length has a value which is an int
	max_intron_length has a value which is an int
	no_spliced_alignment has a value which is a kb_hisat2.bool
	transcriptome_mapping_only has a value which is a kb_hisat2.bool
	tailor_alignments has a value which is a string
bool is an int
ResultsToReport is a reference to a hash where the following keys are defined:
	report_name has a value which is a string
	report_ref has a value which is a string


=end text

=item Description



=back

=cut

 sub run_hisat2
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function run_hisat2 (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to run_hisat2:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'run_hisat2');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "kb_hisat2.run_hisat2",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'run_hisat2',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method run_hisat2",
					    status_line => $self->{client}->status_line,
					    method_name => 'run_hisat2',
				       );
    }
}
 
  
sub status
{
    my($self, @args) = @_;
    if ((my $n = @args) != 0) {
        Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
                                   "Invalid argument count for function status (received $n, expecting 0)");
    }
    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
        method => "kb_hisat2.status",
        params => \@args,
    });
    if ($result) {
        if ($result->is_error) {
            Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
                           code => $result->content->{error}->{code},
                           method_name => 'status',
                           data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
                          );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method status",
                        status_line => $self->{client}->status_line,
                        method_name => 'status',
                       );
    }
}
   

sub version {
    my ($self) = @_;
    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
        method => "kb_hisat2.version",
        params => [],
    });
    if ($result) {
        if ($result->is_error) {
            Bio::KBase::Exceptions::JSONRPC->throw(
                error => $result->error_message,
                code => $result->content->{code},
                method_name => 'run_hisat2',
            );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(
            error => "Error invoking method run_hisat2",
            status_line => $self->{client}->status_line,
            method_name => 'run_hisat2',
        );
    }
}

sub _validate_version {
    my ($self) = @_;
    my $svr_version = $self->version();
    my $client_version = $VERSION;
    my ($cMajor, $cMinor) = split(/\./, $client_version);
    my ($sMajor, $sMinor) = split(/\./, $svr_version);
    if ($sMajor != $cMajor) {
        Bio::KBase::Exceptions::ClientServerIncompatible->throw(
            error => "Major version numbers differ.",
            server_version => $svr_version,
            client_version => $client_version
        );
    }
    if ($sMinor < $cMinor) {
        Bio::KBase::Exceptions::ClientServerIncompatible->throw(
            error => "Client minor version greater than Server minor version.",
            server_version => $svr_version,
            client_version => $client_version
        );
    }
    if ($sMinor > $cMinor) {
        warn "New client version available for kb_hisat2::kb_hisat2Client\n";
    }
    if ($sMajor == 0) {
        warn "kb_hisat2::kb_hisat2Client version is $svr_version. API subject to change.\n";
    }
}

=head1 TYPES



=head2 bool

=over 4



=item Description

indicates true or false values, false <= 0, true >=1


=item Definition

=begin html

<pre>
an int
</pre>

=end html

=begin text

an int

=end text

=back



=head2 ResultsToReport

=over 4



=item Description

Object for Report type


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
report_name has a value which is a string
report_ref has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
report_name has a value which is a string
report_ref has a value which is a string


=end text

=back



=head2 Hisat2Params

=over 4



=item Description

Input for hisat2.
ws_name = the workspace name provided by the narrative for storing output.
sampleset_ref = the workspace reference for the sampleset of reads to align.
genome_ref = the workspace reference for the reference genome that HISAT2 will align against.
alignmentset_name = the name of the alignment set object to create.
num_threads = the number of threads to tell hisat to use (NOT USER SET?)
quality_score =
skip =
trim3 =
trim5 =
np =
minins =
maxins =
orientation =
min_intron_length =
max_intron_length =
no_spliced_alignment =
transcriptome_mapping_only =
tailor_alignments =


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
ws_name has a value which is a string
alignmentset_name has a value which is a string
sampleset_ref has a value which is a string
genome_ref has a value which is a string
num_threads has a value which is an int
quality_score has a value which is a string
skip has a value which is an int
trim3 has a value which is an int
trim5 has a value which is an int
np has a value which is an int
minins has a value which is an int
maxins has a value which is an int
orientation has a value which is a string
min_intron_length has a value which is an int
max_intron_length has a value which is an int
no_spliced_alignment has a value which is a kb_hisat2.bool
transcriptome_mapping_only has a value which is a kb_hisat2.bool
tailor_alignments has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
ws_name has a value which is a string
alignmentset_name has a value which is a string
sampleset_ref has a value which is a string
genome_ref has a value which is a string
num_threads has a value which is an int
quality_score has a value which is a string
skip has a value which is an int
trim3 has a value which is an int
trim5 has a value which is an int
np has a value which is an int
minins has a value which is an int
maxins has a value which is an int
orientation has a value which is a string
min_intron_length has a value which is an int
max_intron_length has a value which is an int
no_spliced_alignment has a value which is a kb_hisat2.bool
transcriptome_mapping_only has a value which is a kb_hisat2.bool
tailor_alignments has a value which is a string


=end text

=back



=cut

package kb_hisat2::kb_hisat2Client::RpcClient;
use base 'JSON::RPC::Client';
use POSIX;
use strict;

#
# Override JSON::RPC::Client::call because it doesn't handle error returns properly.
#

sub call {
    my ($self, $uri, $headers, $obj) = @_;
    my $result;


    {
	if ($uri =~ /\?/) {
	    $result = $self->_get($uri);
	}
	else {
	    Carp::croak "not hashref." unless (ref $obj eq 'HASH');
	    $result = $self->_post($uri, $headers, $obj);
	}

    }

    my $service = $obj->{method} =~ /^system\./ if ( $obj );

    $self->status_line($result->status_line);

    if ($result->is_success) {

        return unless($result->content); # notification?

        if ($service) {
            return JSON::RPC::ServiceObject->new($result, $self->json);
        }

        return JSON::RPC::ReturnObject->new($result, $self->json);
    }
    elsif ($result->content_type eq 'application/json')
    {
        return JSON::RPC::ReturnObject->new($result, $self->json);
    }
    else {
        return;
    }
}


sub _post {
    my ($self, $uri, $headers, $obj) = @_;
    my $json = $self->json;

    $obj->{version} ||= $self->{version} || '1.1';

    if ($obj->{version} eq '1.0') {
        delete $obj->{version};
        if (exists $obj->{id}) {
            $self->id($obj->{id}) if ($obj->{id}); # if undef, it is notification.
        }
        else {
            $obj->{id} = $self->id || ($self->id('JSON::RPC::Client'));
        }
    }
    else {
        # $obj->{id} = $self->id if (defined $self->id);
	# Assign a random number to the id if one hasn't been set
	$obj->{id} = (defined $self->id) ? $self->id : substr(rand(),2);
    }

    my $content = $json->encode($obj);

    $self->ua->post(
        $uri,
        Content_Type   => $self->{content_type},
        Content        => $content,
        Accept         => 'application/json',
	@$headers,
	($self->{token} ? (Authorization => $self->{token}) : ()),
    );
}



1;
